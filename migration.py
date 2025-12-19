import subprocess
import os
import tempfile
import psycopg2
import logging

def get_conn_string(conn_details):
    return f"host={conn_details['host']} port={conn_details['port']} dbname={conn_details['dbname']} user={conn_details['user']} password={conn_details['password']}"

def run_command(cmd, env, log_callback):
    """Runs a shell command and streams stdout/stderr to the log callback."""
    masked_cmd = " ".join([c if i != 0 or 'PGPASSWORD' not in env else '****' for i, c in enumerate(cmd)])
    # Simplified masking for now as PGPASSWORD is in env, not cmd
    log_callback(f"Executing: {' '.join(cmd[:1])} ...") 
    
    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    for line in iter(process.stdout.readline, ""):
        if line:
            log_callback(line.strip())
            
    process.stdout.close()
    return_code = process.wait()
    if return_code != 0:
        raise Exception(f"Command failed with exit code {return_code}")

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
    # Use NamedTemporaryFile for better lifecycle management
    with tempfile.NamedTemporaryFile(suffix=".dump", delete=False) as tmp_file:
        dump_file = tmp_file.name

    try:
        # 1. pg_dump from Source
        mode_str = "Schema Only" if schema_only else "Full (Schema + Data)"
        log_callback(f"PHASE:DUMPING|Starting dump ({mode_str}) from {source['host']}...")
        
        env_source = os.environ.copy()
        env_source['PGPASSWORD'] = source['password']
        
        dump_cmd = [
            'pg_dump',
            '-v', # Verbose for better logging
            '-h', source['host'],
            '-p', source['port'],
            '-U', source['user'],
            '-Fc', # Custom format
            '-f', dump_file,
            source['dbname']
        ]
        
        if schema_only:
            dump_cmd.insert(5, '-s')

        run_command(dump_cmd, env_source, log_callback)
        log_callback("Dump completed successfully.")
        
        # 2. Drop tables on Target
        log_callback("PHASE:DROPPING|Preparing target database (dropping existing tables)...")
        drop_public_tables(target, log_callback)
        
        # 3. pg_restore to Target
        log_callback(f"PHASE:RESTORING|Starting restore to {target['host']}...")
        
        env_target = os.environ.copy()
        env_target['PGPASSWORD'] = target['password']
        
        restore_cmd = [
            'pg_restore',
            '-v', # Verbose
            '-h', target['host'],
            '-p', target['port'],
            '-U', target['user'],
            '-d', target['dbname'],
            dump_file
        ]
        
        run_command(restore_cmd, env_target, log_callback)
        log_callback("Restore completed successfully.")
        
        return True, "Migration completed successfully!"
        
    except Exception as e:
        log_callback(f"ERROR: Migration Failed - {str(e)}")
        return False, str(e)
    finally:
        if os.path.exists(dump_file):
            try:
                os.remove(dump_file)
                log_callback("Cleaned up temporary resources.")
            except:
                pass

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
