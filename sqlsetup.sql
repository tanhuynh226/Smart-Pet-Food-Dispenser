USE dispenser;

CREATE TABLE Gen (
    phone_number bigint,
    calibrate_distance int,
    row_num int,
    primary key(row_num)
);

CREATE TABLE Dispenser1 (
	detect_pet int,
    pet_breed varchar(255),
    dispenses_per_day int,
    amount_dispensed float,
    increments int,
    time_between_increments float,
    row_num int,
    primary key(row_num)
);

CREATE TABLE Dispenser2 (
	detect_pet int,
    pet_breed varchar(255),
    dispenses_per_day int,
    amount_dispensed float,
    increments int,
    time_between_increments float,
    row_num int,
    primary key(row_num)
);



INSERT INTO Gen (phone_number, calibrate_distance, row_num) VALUES 
	(14086149226, 0, 1);
    
INSERT INTO Dispenser1 (detect_pet, pet_breed, dispenses_per_day, amount_dispensed, increments, time_between_increments, row_num) VALUES
	(0, "Cat", 1, 5, 1, 5, 1);

INSERT INTO Dispenser2 (detect_pet, pet_breed, dispenses_per_day, amount_dispensed, increments, time_between_increments, row_num) VALUES
	(0, "German Shepherd", 1, 5, 1, 5, 1);
    
SELECT dispenses_per_day, amount_dispensed, increments, time_between_increments FROM Dispenser1;

UPDATE Gen SET phone_number = 456 WHERE row_num = 1;

SELECT phone_number FROM Gen;