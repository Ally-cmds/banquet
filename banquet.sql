CREATE DATABASE Banquet_db;
USE Banquet_db;

#creating tables
CREATE TABLE Banquets (
    BIN INT AUTO_INCREMENT PRIMARY KEY,
    Staff_Email VARCHAR(150) NOT NULL CHECK (Staff_Email LIKE '%@%'),
    Banquet_Name VARCHAR(150) NOT NULL,
    Date DATE NOT NULL,
    Time TIME NOT NULL,
    Address TEXT NOT NULL,
    Location TEXT NOT NULL,
    c_fname VARCHAR(100) NOT NULL CHECK (c_fname NOT REGEXP '[^A-Za-z]'),
    c_lname VARCHAR(100) NOT NULL CHECK (c_lname NOT REGEXP '[^A-Za-z]'),
    availability VARCHAR(100) NOT NULL CHECK (availability IN ('Y', 'N')),
    quota INT NOT NULL
);


CREATE TABLE Attendees (
    AttendeeID INT PRIMARY KEY,
    a_fname VARCHAR(100) NOT NULL,
    a_lname VARCHAR(100) NOT NULL,
    a_phno VARCHAR(15) NOT NULL,
    a_addrs TEXT NOT NULL,
    attendee_type VARCHAR(10) NOT NULL CHECK(attendee_type IN('student','staff','guest','others')),
    a_org VARCHAR(100) NOT NULL CHECK (a_org IN ('PolyU','SPEED','HKCC','Others')),
    a_email VARCHAR(150) NOT NULL CHECK (a_email LIKE '%_@%.__%'),
    a_pw VARCHAR(100) NOT NULL,
    registrationDate DATETIME NOT NULL,
    AccountStatus VARCHAR(10) NOT NULL CHECK (AccountStatus IN ('Active', 'Inactive')),
    BIN INT,
    FOREIGN KEY (BIN) REFERENCES Banquets(BIN) ON DELETE RESTRICT
);

CREATE TABLE Meals (
    mealID INT NOT NULL,
    BIN INT NOT NULL,
    Type VARCHAR(10) NOT NULL CHECK (Type IN ('fish', 'chicken', 'beef', 'vegetarian')),
    Price NUMERIC NOT NULL,
    Special_cuisine TEXT NOT NULL,
    DishName VARCHAR(150) NOT NULL,
    PRIMARY KEY (mealID),
    FOREIGN KEY (BIN) REFERENCES Banquets(BIN) ON DELETE RESTRICT
);

CREATE TABLE Event (
    EventID INT NOT NULL PRIMARY KEY,
    BIN INT NOT NULL,
    Date DATE    NOT NULL,
    Time TIME   NOT NULL,
    price NUMERIC NOT NULL,
    content VARCHAR(50) NOT NULL,
    size INT NOT NULL,
    guests INT NOT NULL,
    person_in_charge  Varchar(100)   NOT NULL,
    FOREIGN KEY (BIN) REFERENCES Banquets(BIN) ON DELETE RESTRICT
);

CREATE TABLE Equipment (
    EquipmentID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Category VARCHAR(100) NOT NULL,
    Conditions VARCHAR(100) NOT NULL CHECK (Conditions IN ('Available', 'Unavailable')),
    Bought_date DATE
);

CREATE TABLE Waitlist (
   WaitlistID INT PRIMARY KEY,
   BIN INT NOT NULL,
   WaitlistDate DATE NOT NULL,
   Status VARCHAR(20) NOT NULL,
   FOREIGN KEY (BIN) REFERENCES Banquets(BIN) ON DELETE RESTRICT
);

CREATE TABLE Feedback (
   FeedbackID INT PRIMARY KEY,
   BIN INT NOT NULL,
   AttendeeID INT NOT NULL,
   Rating INT NOT NULL,
   Comments VARCHAR(255) NOT NULL,
   FeedbackDate DATE NOT NULL,
   FOREIGN KEY (AttendeeID) REFERENCES Attendees(AttendeeID) ON DELETE RESTRICT,
   FOREIGN KEY (BIN) REFERENCES Banquets(BIN) ON DELETE RESTRICT
);

CREATE TABLE Reservation (
    ReservationID INT AUTO_INCREMENT PRIMARY KEY,
    BIN INT NOT NULL,
    AttendeeID INT NOT NULL,
    MealID INT NOT NULL,
    DrinkChoice VARCHAR(50),
    Remarks VARCHAR(255),
    Status VARCHAR(20) NOT NULL,
    RegistrationDate DATE NOT NULL,
    UpdateDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (BIN) REFERENCES Banquets(BIN) ON DELETE RESTRICT,
    FOREIGN KEY (AttendeeID) REFERENCES Attendees(AttendeeID) ON DELETE RESTRICT,
    FOREIGN KEY (MealID) REFERENCES Meals(MealID) ON DELETE RESTRICT
);

CREATE TABLE Notification (
   NotificationID INT PRIMARY KEY,
   AttendeeID INT NOT NULL,
   Message VARCHAR(255) NOT NULL,
   NotificationDate DATE NOT NULL,
   NotificationType VARCHAR(50) NOT NULL,
   FOREIGN KEY (AttendeeID) REFERENCES Attendees(AttendeeID) ON DELETE RESTRICT
);

#insert sample data
INSERT INTO Banquets(BIN, Staff_Email, Banquet_name, Date, Time, Address, Location, C_fname, C_lname, Availability, Quota) VALUES
(1, 'alice.smith@example.com', 'Spring Gala', '2024-05-15', '18:00:00', '123 Celebration Ave, Cityville', 'City Center', 'Alice', 'Smith', 'Y', 5),
(2, 'bob.johnson@example.com', 'Summer Fest', '2024-06-20', '17:30:00', '456 Summer St, Townsville', 'Town Hall', 'Bob', 'Johnson', 'Y', 200),
(3, 'charlie.brown@example.com', 'Autumn Affair', '2024-09-10', '19:00:00', '789 Autumn Ln, Villageburg', 'Community Park', 'Charlie', 'Brown', 'N', 100),
(4, 'diana.white@example.com', 'Winter Wonderland', '2024-12-05', '18:30:00', '101 Winter Blvd, Snowtown', 'Convention Center', 'Diana', 'White', 'Y', 250),
(5, 'ethan.williams@example.com', 'Charity Ball', '2024-04-25', '20:00:00', '202 Charity Rd, Fundsville', 'Grand Hall', 'Ethan', 'Williams', 'Y', 300);

INSERT INTO Meals (mealID, BIN, Type, Price, Special_cuisine, DishName) VALUES
(11, 1, 'fish', 15.99, 'Italian', 'Bruschetta'),
(22, 1, 'vegetarian', 25.50, 'French', 'Coq au Vin'),
(33, 1, 'beef', 8.75, 'Italian', 'Tiramisu'),
(44, 2, 'chicken', 12.00, 'Mexican', 'Guacamole'),
(55, 2, 'beef', 22.00, 'Mexican', 'Tacos al Pastor'),
(66, 3, 'vegetarian', 27.50, 'Indian', 'Butter Chicken'),
(77, 4, 'fish', 14.00, 'American', 'Buffalo Wings'),
(88, 5, 'beef', 10.50, 'French', 'Crème Brûlée'),
(99, 5, 'vegetarian', 30.00, 'Italian', 'Lasagna');

INSERT INTO Attendees (AttendeeID, BIN, a_fname, a_lname, a_phno, a_addrs, attendee_type, a_org, a_email, a_pw, registrationDate, AccountStatus) VALUES
(4001, 1, 'John', 'Doe', '12345678', '123 Main St, Cityville', 'staff', 'PolyU', 'john.doe@example.com', 'password123', '2024-05-10', 'Active'),
(4002, 1, 'Jane', 'Smith', '87654321', '456 Elm St, Townsville', 'guest', 'SPEED', 'jane.smith@example.com', 'password456', '2024-05-05', 'Inactive'),
(4003, 5, 'Alice', 'Johnson', '23456789', '789 Oak St, Villageville', 'student', 'HKCC', 'alice.johnson@example.com', 'password789', '2024-03-29', 'Active'),
(4004, 2, 'Bob', 'Williams', '34567890', '321 Pine St, Hamletville', 'guest', 'Others', 'bob.williams@example.com', 'password321', '2024-06-10', 'Active'),
(4005, 2, 'Carol', 'Brown', '45678901', '654 Maple St, Boroughville', 'others', 'Others', 'carol.brown@example.com', 'password654', '2024-06-11', 'Inactive'),
(4006, 3, 'David', 'Davis', '56789012', '987 Cedar St, Metropolis', 'student', 'Others', 'david.davis@example.com', 'password987', '2024-09-06', 'Active');

INSERT INTO Event (EventID, BIN, Date, Time, Price, Content, Size, Guests, Person_in_charge) VALUES
(101, 1, '2024-05-15', '19:00:00', 500.00, 'Live Music Performance', 500, 300, 'Alice Smith'),
(102, 2, '2024-06-20', '18:00:00', 750.00, 'Fireworks Display', 200, 150, 'Bob Johnson'),
(103, 1, '2024-05-15', '20:30:00', 300.00, 'Spring-themed Decorations', 500, 300, 'Alice Smith'),
(104, 4, '2024-12-05', '20:00:00', 600.00, 'Hot Chocolate Bar', 150, 120, 'Diana White'),
(105, 5, '2024-04-25', '20:20:00', 400.00, 'Dance Floor', 80, 60, 'Ethan Williams');

INSERT INTO Equipment (EquipmentID, Name, Category, Conditions, Bought_date) VALUES
(1001, 'Projector', 'Audio/Visual', 'Available', '2023-01-15'),
(1002, 'Microphone', 'Audio/Visual', 'Unavailable', '2023-03-22'),
(1003, 'Stage Lights', 'Lighting', 'Available', '2022-11-05'),
(1004, 'Sound System', 'Audio/Visual', 'Available', '2023-05-30'),
(1005, 'Chairs', 'Furniture', 'Available', '2022-08-12'),
(1006, 'Tables', 'Furniture', 'Unavailable', '2023-02-10'),
(1007, 'Whiteboard', 'Office Supplies', 'Available', '2023-04-15'),
(1008, 'Laptop', 'Computers', 'Available', '2023-06-20'),
(1009, 'Camera', 'Audio/Visual', 'Available', '2022-12-01'),
(1010, 'Projector Screen', 'Audio/Visual', 'Unavailable', '2023-07-10');


INSERT INTO Waitlist (WaitlistID, BIN, WaitlistDate, Status) VALUES
(3001, 1, '2024-3-9', 'Pending'),
(3002, 2, '2024-11-18', 'Confirmed'),
(3003, 3, '2024-6-9', 'Pending'),
(3004, 5, '2024-11-10', 'Cancelled'),
(3005, 5, '2024-5-12', 'Confirmed');

INSERT INTO Feedback (FeedbackID, BIN, AttendeeID, Rating, Comments, FeedbackDate) VALUES
(8001, 1, 4002, 3, 'The staff were polite, but the service was slow. We had to wait a long time for our requests to be addressed, and some orders were forgotten.', '2024-05-25'),
(8002, 1, 4001, 5, 'We felt that the service provided excellent value for the price. There were no hidden costs, and the quality of service justified the expense.', '2024-05-18'),
(8003, 2, 4005, 4, 'The staff were incredibly professional and attentive. They ensured that all our guests were well taken care of and responded promptly to any requests.', '2024-06-30'),
(8004, 5, 4003, 4, 'Great event, but the venue was a bit crowded.', '2024-04-30');

INSERT INTO Reservation (ReservationID, BIN, AttendeeID, MealID, DrinkChoice, Remarks, Status, RegistrationDate, UpdateDate) VALUES
(5001, 1, 4001,22, 'Red Wine', 'Window seat requested', 'Confirmed', '2024-05-10', '2024-05-11'),
(5002, 1, 4002,22, 'Sparkling Water', 'No allergies', 'Pending', '2024-05-05', '2024-05-06'),
(5003, 2, 4004, 55, 'Beer', 'Vegetarian meal', 'Confirmed', '2024-06-10', '2024-06-11'),
(5004, 2, 4005, 55,'Coke', 'Birthday celebration', 'Cancelled', '2024-06-11', '2024-06-12'),
(5005, 3, 4006, 66, 'Tea', 'Bring a friend', 'Confirmed', '2024-09-06', '2024-09-07');
 

 INSERT INTO Notification (NotificationID, AttendeeID, Message, NotificationDate, NotificationType) VALUES
(6001, 4001, 'Your reservation has been confirmed.', '2024-01-15', 'Reservation Confirmation'),
(6002, 4002, 'Your meal choice has been updated.', '2024-01-16', 'Meal Update'),
(6003, 4003, 'Reminder: Your event is coming up soon.', '2024-02-01', 'Reminder'),
(6004, 4004, 'Your reservation has been cancelled.', '2024-02-12', 'Cancellation'),
(6005, 4006, 'Thank you for attending our event!', '2024-03-06', 'Thank You');

#to see if inserted succesfully
SELECT * FROM Banquets;
SELECT * FROM Meals;
SELECT * FROM attendees;
SELECT * FROM event;
SELECT * FROM equipment;
SELECT * FROM waitlist;
SELECT * FROM feedback;
SELECT * FROM reservation;
SELECT * FROM notification;