-- Student Freelance Marketplace
-- Nine tables from the project proposal.
--
-- Neon is a cloud PostgreSQL database, not MySQL.
-- Primary keys, foreign keys, one-to-many, and many-to-many
-- work the same way. The usual syntax difference is:
--   PostgreSQL:  student_id SERIAL PRIMARY KEY
--   MySQL:       student_id INT AUTO_INCREMENT PRIMARY KEY
--
-- PostgreSQL stores unquoted names in lowercase.
-- Writing Student or student refers to the same table.

-- Child tables are dropped first. A parent cannot be dropped
-- while a foreign key still points at it.
DROP TABLE IF EXISTS Review;
DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS Contract;
DROP TABLE IF EXISTS Proposal;
DROP TABLE IF EXISTS Project;
DROP TABLE IF EXISTS StudentSkill;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Skill;
DROP TABLE IF EXISTS Client;

CREATE TABLE Student (
    student_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    university VARCHAR(120) NOT NULL,
    bio TEXT
);

CREATE TABLE Skill (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(80) NOT NULL UNIQUE
);

-- Many-to-many link.
-- One student can have many skills, and one skill can belong to many students.
-- The two foreign keys together are the primary key, so the same pair
-- cannot be stored twice.
CREATE TABLE StudentSkill (
    student_id INT NOT NULL,
    skill_id INT NOT NULL,
    PRIMARY KEY (student_id, skill_id),
    FOREIGN KEY (student_id) REFERENCES Student (student_id),
    FOREIGN KEY (skill_id) REFERENCES Skill (skill_id)
);

CREATE TABLE Client (
    client_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    company VARCHAR(120)
);

-- One-to-many: one client posts many projects.
-- Project.client_id is the foreign key.
CREATE TABLE Project (
    project_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    budget DECIMAL(10, 2) NOT NULL CHECK (budget > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'in_progress', 'completed')),
    FOREIGN KEY (client_id) REFERENCES Client (client_id)
);

-- One project has many proposals.
-- One student has many proposals.
-- UNIQUE (project_id, student_id) means one proposal per student per project.
CREATE TABLE Proposal (
    proposal_id SERIAL PRIMARY KEY,
    project_id INT NOT NULL,
    student_id INT NOT NULL,
    cover_letter TEXT NOT NULL,
    bid_amount DECIMAL(10, 2) NOT NULL CHECK (bid_amount > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'rejected')),
    FOREIGN KEY (project_id) REFERENCES Project (project_id),
    FOREIGN KEY (student_id) REFERENCES Student (student_id),
    UNIQUE (project_id, student_id)
);

-- Accepting a proposal creates one contract.
-- UNIQUE on project_id and proposal_id keeps that one-to-one.
-- student_id and client_id are stored here so the contract itself
-- shows the two people who agreed.
CREATE TABLE Contract (
    contract_id SERIAL PRIMARY KEY,
    project_id INT NOT NULL UNIQUE,
    proposal_id INT NOT NULL UNIQUE,
    student_id INT NOT NULL,
    client_id INT NOT NULL,
    agreed_amount DECIMAL(10, 2) NOT NULL CHECK (agreed_amount > 0),
    start_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'completed')),
    FOREIGN KEY (project_id) REFERENCES Project (project_id),
    FOREIGN KEY (proposal_id) REFERENCES Proposal (proposal_id),
    FOREIGN KEY (student_id) REFERENCES Student (student_id),
    FOREIGN KEY (client_id) REFERENCES Client (client_id)
);

-- One-to-many: one contract can have several payments.
CREATE TABLE Payment (
    payment_id SERIAL PRIMARY KEY,
    contract_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    payment_date DATE NOT NULL,
    FOREIGN KEY (contract_id) REFERENCES Contract (contract_id)
);

-- One-to-one: contract_id is UNIQUE, so a contract has at most one review.
CREATE TABLE Review (
    review_id SERIAL PRIMARY KEY,
    contract_id INT NOT NULL UNIQUE,
    student_id INT NOT NULL,
    client_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    FOREIGN KEY (contract_id) REFERENCES Contract (contract_id),
    FOREIGN KEY (student_id) REFERENCES Student (student_id),
    FOREIGN KEY (client_id) REFERENCES Client (client_id)
);
