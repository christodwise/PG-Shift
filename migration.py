import subprocess
import os
import tempfile
import psycopg2
import logging

def get_conn_string(conn_details):
    return f"host={conn_details['host']} port={conn_details['port']} dbname={conn_details['dbname']} user={conn_details['user']} password={conn_details['password']}"

def run_command(cmd, env, log_callback):
    """Runs a shell command and streams stdout/stderr to the log callback."""
    # Mask password in logs
    masked_cmd = " ".join(cmd)
    if 'PGPASSWORD' in env:
         pass # Environment variables are not printed in the command string usually, but be careful
    
    log_callback(f"Running: {masked_cmd}")
    
    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    for line in process.stdout:
        log_callback(line.strip())
        
    process.wait()
    if process.returncode != 0:
        raise Exception(f"Command failed with exit code {process.returncode}")

def drop_public_tables(target_conn_details, log_callback):
    log_callback("Connecting to target to drop tables...")
    try:
        conn = psycopg2.connect(
            host=target_conn_details['host'],
            port=target_conn_details['port'],
            dbname=target_conn_details['dbname'],
            user=target_conn_details['user'],
            password=target_conn_details['password']
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        sql = """
        DO
        $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END
        $$;
        """
        log_callback("Executing DROP TABLE script...")
        cur.execute(sql)
        log_callback("All public tables dropped successfully.")
        
        cur.close()
        conn.close()
    except Exception as e:
        log_callback(f"Error dropping tables: {str(e)}")
        raise e

def run_migration(source, target, log_callback, schema_only=False):
    dump_file = tempfile.mktemp(suffix=".dump")
    
    try:
        # 1. pg_dump from Source
        mode_str = "Schema Only" if schema_only else "Full (Schema + Data)"
        log_callback(f"Starting dump ({mode_str}) from {source['host']}:{source['port']}/{source['dbname']}...")
        
        env_source = os.environ.copy()
        env_source['PGPASSWORD'] = source['password']
        
        dump_cmd = [
            'pg_dump',
            '-h', source['host'],
            '-p', source['port'],
            '-U', source['user'],
            '-Fc', # Custom format
            '-f', dump_file,
            source['dbname']
        ]
        
        if schema_only:
            dump_cmd.insert(5, '-s') # Add -s before -Fc or anywhere valid

        
        run_command(dump_cmd, env_source, log_callback)
        log_callback("Dump completed.")
        
        # 2. Drop tables on Target
        drop_public_tables(target, log_callback)
        
        # 3. pg_restore to Target
        log_callback(f"Starting restore to {target['host']}:{target['port']}/{target['dbname']}...")
        
        env_target = os.environ.copy()
        env_target['PGPASSWORD'] = target['password']
        
        restore_cmd = [
            'pg_restore',
            '-h', target['host'],
            '-p', target['port'],
            '-U', target['user'],
            '-d', target['dbname'],
            dump_file
        ]
        
        run_command(restore_cmd, env_target, log_callback)
        log_callback("Restore completed successfully.")
        
        return True, "Migration successful"
        
    except Exception as e:
        log_callback(f"Migration Failed: {str(e)}")
        return False, str(e)
    finally:
        if os.path.exists(dump_file):
            os.remove(dump_file)
            log_callback("Cleaned up temporary dump file.")

def test_connection(conn_details):
    """Tests connection and returns Postgres version string."""
    try:
        conn = psycopg2.connect(
            host=conn_details['host'],
            port=conn_details['port'],
            dbname=conn_details['dbname'],
            user=conn_details['user'],
            password=conn_details['password'],
            connect_timeout=5
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        conn.close()
        return True, version
    except Exception as e:
        return False, str(e)

def get_db_stats(conn_details):
    """Returns basic stats about the database."""
    try:
        conn = psycopg2.connect(
            host=conn_details['host'],
            port=conn_details['port'],
            dbname=conn_details['dbname'],
            user=conn_details['user'],
            password=conn_details['password']
        )
        cur = conn.cursor()
        
        # Schema count
        cur.execute("SELECT count(*) FROM information_schema.schemata;")
        schema_count = cur.fetchone()[0]
        
        # Table count
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog');")
        table_count = cur.fetchone()[0]
        
        # Approx Row Count (fastest way)
        cur.execute("SELECT SUM(reltuples) AS approximate_row_count FROM pg_class WHERE relkind = 'r';")
        row_count = cur.fetchone()[0]
        if row_count is None: row_count = 0
        
        conn.close()
        
        return {
            'schemas': schema_count,
            'tables': table_count,
            'rows': int(row_count)
        }
    except Exception as e:
        raise e

def get_local_pg_dump_version():
    """Returns the major version of the local pg_dump binary."""
    try:
        output = subprocess.check_output(['pg_dump', '--version'], text=True)
        # Output format: pg_dump (PostgreSQL) 14.17 (Homebrew)
        # We want "14"
        import re
        match = re.search(r'(\d+)\.', output)
        if match:
            return int(match.group(1))
        return 0
    except Exception:
        return 0

def preflight_check(source, target):
    """Runs checks before migration."""
    checks = []
    
    # Check 0: Local Binary Version
    local_ver = get_local_pg_dump_version()
    if local_ver == 0:
         checks.append({'status': 'fail', 'msg': "Could not find 'pg_dump'. Is it installed?"})
    else:
         checks.append({'status': 'pass', 'msg': f"Local pg_dump version: {local_ver}"})
    
    # Check 1: Source Connectivity
    s_ok, s_ver = test_connection(source)
    if s_ok:
        checks.append({'status': 'pass', 'msg': f"Source Connected: {s_ver.split(' ')[0]}..."})
        
        # Check Version Mismatch
        # s_ver format: PostgreSQL 17.7 (Ubuntu 17.7-...)
        import re
        s_match = re.search(r'PostgreSQL (\d+)', s_ver)
        if s_match and local_ver > 0:
            server_major = int(s_match.group(1))
            if local_ver < server_major:
                checks.append({'status': 'fail', 'msg': f"Version Mismatch: Local pg_dump ({local_ver}) < Source DB ({server_major}). Update local Postgres tools!"})
            else:
                checks.append({'status': 'pass', 'msg': "Binary Compatibility Verified"})
    else:
        checks.append({'status': 'fail', 'msg': f"Source Failed: {s_ver}"})
        return checks # Stop if source fails
        
    # Check 2: Target Connectivity
    t_ok, t_ver = test_connection(target)
    if t_ok:
        checks.append({'status': 'pass', 'msg': f"Target Connected: {t_ver.split(' ')[0]}..."})
    else:
        checks.append({'status': 'fail', 'msg': f"Target Failed: {t_ver}"})
    
    return checks
