USE dispenser;

CREATE TABLE Gen (
    phone_number bigint,
    calibrate_distance bool
);

CREATE TABLE Dispenser1 (
	detect_pet bool,
    pet_breed varchar(255),
    dispenses_per_day int,
    amount_dispensed float,
    increments int,
    time_between_increments int
);

CREATE TABLE Dispenser2 (
	detect_pet bool,
    pet_breed varchar(255),
    dispenses_per_day int,
    amount_dispensed float,
    increments int,
    time_between_increments int
);

INSERT INTO Gen (phone_number, calibrate_distance) VALUES 
	(14086149226, 0);
    
INSERT INTO Dispenser1 (detect_pet, pet_breed, dispenses_per_day, amount_dispensed, increments, time_between_increments) VALUES
	(0, "", 1, 5, 1, 5);

INSERT INTO Dispenser2 (detect_pet, pet_breed, dispenses_per_day, amount_dispensed, increments, time_between_increments) VALUES
	(0, "", 1, 5, 1, 5);
    
SELECT dispenses_per_day, amount_dispensed, increments, time_between_increments FROM Dispenser1;