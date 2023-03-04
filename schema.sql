CREATE TABLE "users" (
	"id"	INTEGER NOT NULL UNIQUE,
	"email"	TEXT NOT NULL UNIQUE,
	"phone"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
	"account_type"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "qualifications" (
	"id"	INTEGER NOT NULL,
	"qualification"	TEXT NOT NULL UNIQUE,
	"level"	INT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "applicants" (
	"user_id"	INTEGER NOT NULL UNIQUE,
	"first_name"	TEXT NOT NULL,
	"surname"	TEXT NOT NULL,
	"other_name"	TEXT,
	"qualification_id"	INT NOT NULL,
	"dob"	DATE NOT NULL,
	"profile_picture"	TEXT NOT NULL,
	"resume"	TEXT NOT NULL,
	FOREIGN KEY("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY("user_id"),
	FOREIGN KEY("qualification_id") REFERENCES "qualifications"("id")
);

CREATE TABLE "employers" (
	"user_id"	INTEGER NOT NULL UNIQUE,
	"org_name"	TEXT NOT NULL,
	"org_profile_picture"	TEXT NOT NULL,
	FOREIGN KEY("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY("user_id")
);

INSERT INTO qualifications(qualification, level)
VALUES
("Doctorate",	1),
("Master's Degree",	2),
("Postgraduate Diploma",	3),
("Bachelor's Degree",	4),
("Higher National Diploma",	5),
("National Diploma",	6),
("Undergraduate",	7),
("Secondary Schl Cert.",	8),
("Primary Schl Cert.",	9);