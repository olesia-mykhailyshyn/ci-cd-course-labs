CREATE TABLE tutors (
    id serial PRIMARY KEY,
    name text NOT NULL,
    subject text NOT NULL
);

CREATE TABLE lessons (
    id serial PRIMARY KEY,
    tutor_id integer NOT NULL REFERENCES tutors (id),
    slot text NOT NULL,
    student text NOT NULL,
    UNIQUE (tutor_id, slot)
);

INSERT INTO tutors (name, subject) VALUES
    ('Olena Kovalenko', 'English'),
    ('Marko Shevchenko', 'Mathematics'),
    ('Iryna Bondar', 'Spanish');
