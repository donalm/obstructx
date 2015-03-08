-- test database setup

CREATE TABLE AppUser (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    dob date DEFAULT NULL
);

INSERT INTO AppUser (username, name, surname, dob) VALUES ('batman', 'Bruce', 'Wayne', '1939-11-01');


CREATE TABLE Car (
    id SERIAL PRIMARY KEY,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    registration TEXT NOT NULL,
    date_of_manufacture date DEFAULT NULL,
    owner_id INTEGER NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES AppUser(id)
);
    

INSERT INTO Car(manufacturer, model, registration, date_of_manufacture, owner_id) values('Ford', 'Focus', 'BAT1', '1999-09-01', 1);

