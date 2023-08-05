import os


def dump_schema(coordinator):
    pg_dump_command = coordinator.schema_dump_statement

    print('Executing %s' % pg_dump_command)

    os.system(pg_dump_command)

    dump_path = coordinator.distribute_path

    f = open(dump_path, "w+")

    for statement in coordinator.reference_statements:
        f.write(statement)

    for statement in coordinator.distribute_statements:
        f.write(statement)

    f.close()


def dump_sequences(coordinator):
    print('Dump sequences')
    sequence_list_query = "SELECT relname FROM pg_class WHERE relkind='S';"
    conn = coordinator.configuration.connection()

    cursor = conn.cursor()
    cursor.execute(sequence_list_query)
    sequences = cursor.fetchall()

    command = '%s --no-owner --format=plain --data-only --file=%s %s' % (
        coordinator.configuration.pg_dump,
        coordinator.sequences_dump_path,
        coordinator.connection_string
    )

    for sequence in sequences:
        command += ' -t %s' % sequence[0]

    os.system(command)


def restore_coordinator(coordinator_host, configuration):
    print('Restore schema on new coordinator')
    dump_path = os.path.join(configuration.dump_folder, 'coordinator_schema.sql')
    distribute_path = os.path.join(configuration.dump_folder, 'coordinator_distribute.sql')
    command = 'psql %s  -a -f %s' % (coordinator_host, dump_path)
    os.system(command)

    command = 'psql %s  -a -f %s' % (coordinator_host, distribute_path)
    os.system(command)


def restore_coordinator_sequences(coordinator):
    print('Restore sequences on new coordinator')
    command = 'psql %s  -a -f %s' % (coordinator.connection_string,
                                     coordinator.sequences_dump_path)
    os.system(command)


def execute_lock_transactions(coordinator, cursor):
    for statement in coordinator.lock_statements:
        retry = 0
        locked = False

        while (retry < 3 and not locked):
            try:
                cursor.execute(statement)
            except psycopg2.errors.LockNotAvailable:
                retry += 1
            else:
                locked = True

        if not locked:
            cursor.execute('END;')
            raise Exception('Could not execute the statement: %s. Please check if you have concurrent writes' % statement)

def lock_tables_before_data_dump(coordinator):
    conn = coordinator.configuration.connection()
    cursor = conn.cursor()

    cursor.execute('BEGIN;')
    cursor.execute("SET lock_timeout='1s';")

    execute_lock_transactions(coordinator, cursor)

    cursor.execute('END;')
