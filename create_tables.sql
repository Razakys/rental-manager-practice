CREATE TABLE Clients (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT    NOT NULL,
    email TEXT    NOT NULL,
    UNIQUE (
        name,
        email
    )
);

CREATE TABLE Spaces (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number INTEGER NOT NULL
                        CHECK (room_number >= 0),
    area        REAL    NOT NULL
                        CHECK (area >= 0),
    location    TEXT    NOT NULL,
    status      TEXT    CHECK (status IN ('свободно', 'занято') ) 
                        NOT NULL,
    UNIQUE (
        location,
        room_number
    )
);


CREATE TABLE Rentals (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id     INTEGER NOT NULL,
    space_id      INTEGER NOT NULL,
    start_date    DATE    NOT NULL,
    end_date      DATE    NOT NULL,
    monthly_price REAL    NOT NULL
                          CHECK (monthly_price >= 0),
    status        TEXT    CHECK (status IN ('активен', 'завершён', 'расторгнут') ) 
                          NOT NULL,
    FOREIGN KEY (
        client_id
    )
    REFERENCES Clients (id),
    FOREIGN KEY (
        space_id
    )
    REFERENCES Spaces (id) 
);
