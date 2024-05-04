DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'oncor') LOOP
        EXECUTE '
            CREATE TABLE oncorfinals.' || r.tablename || ' (
                gid serial not null,
                code varchar (10),
                geom geometry(MULTIPOLYGON, 4326)
            );

            INSERT INTO oncorfinals.' || r.tablename || '(geom)
            SELECT st_multi(st_subdivide((st_dump(st_union(geom))).geom)) as geom
            FROM oncor.' || r.tablename || ';

            ALTER TABLE oncorfinals.' || r.tablename || '
            DROP COLUMN gid;

			UPDATE oncorfinals.' || r.tablename || ' t
            SET code = UPPER(''' || r.tablename || ''');

        ';
    END LOOP;
END $$;