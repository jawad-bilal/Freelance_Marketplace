-- Student Freelance Marketplace
-- Nine tables from the project proposal.
-- Database: Microsoft SQL Server (managed in SSMS)
--
-- Auto numbers use IDENTITY. That is SQL Server's form of:
--   MySQL:       INT AUTO_INCREMENT
--   PostgreSQL:  SERIAL
--
-- Primary keys, foreign keys, one-to-many, and many-to-many
-- are the same ideas as in a MySQL course.

-- Child tables are dropped first. A parent cannot be dropped
-- while a foreign key still points at it.
IF OBJECT_ID('dbo.Review', 'U') IS NOT NULL DROP TABLE dbo.Review;
IF OBJECT_ID('dbo.Payment', 'U') IS NOT NULL DROP TABLE dbo.Payment;
IF OBJECT_ID('dbo.Contract', 'U') IS NOT NULL DROP TABLE dbo.Contract;
IF OBJECT_ID('dbo.Proposal', 'U') IS NOT NULL DROP TABLE dbo.Proposal;
IF OBJECT_ID('dbo.Project', 'U') IS NOT NULL DROP TABLE dbo.Project;
IF OBJECT_ID('dbo.StudentSkill', 'U') IS NOT NULL DROP TABLE dbo.StudentSkill;
IF OBJECT_ID('dbo.Student', 'U') IS NOT NULL DROP TABLE dbo.Student;
IF OBJECT_ID('dbo.Skill', 'U') IS NOT NULL DROP TABLE dbo.Skill;
IF OBJECT_ID('dbo.Client', 'U') IS NOT NULL DROP TABLE dbo.Client;

CREATE TABLE Student (
    student_id INT IDENTITY(1,1) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    university VARCHAR(120) NOT NULL,
    bio NVARCHAR(MAX) NULL
);

CREATE TABLE Skill (
    skill_id INT IDENTITY(1,1) PRIMARY KEY,
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
    client_id INT IDENTITY(1,1) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    company VARCHAR(120) NULL
);

-- One-to-many: one client posts many projects.
-- Project.client_id is the foreign key.
CREATE TABLE Project (
    project_id INT IDENTITY(1,1) PRIMARY KEY,
    client_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description NVARCHAR(MAX) NOT NULL,
    budget DECIMAL(10, 2) NOT NULL CHECK (budget > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'in_progress', 'completed')),
    FOREIGN KEY (client_id) REFERENCES Client (client_id)
);

-- One project has many proposals.
-- One student has many proposals.
-- UNIQUE (project_id, student_id) means one proposal per student per project.
CREATE TABLE Proposal (
    proposal_id INT IDENTITY(1,1) PRIMARY KEY,
    project_id INT NOT NULL,
    student_id INT NOT NULL,
    cover_letter NVARCHAR(MAX) NOT NULL,
    bid_amount DECIMAL(10, 2) NOT NULL CHECK (bid_amount > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'rejected')),
    FOREIGN KEY (project_id) REFERENCES Project (project_id),
    FOREIGN KEY (student_id) REFERENCES Student (student_id),
    CONSTRAINT UQ_Proposal_project_student UNIQUE (project_id, student_id)
);

-- Accepting a proposal creates one contract.
-- UNIQUE on project_id and proposal_id keeps that one-to-one.
CREATE TABLE Contract (
    contract_id INT IDENTITY(1,1) PRIMARY KEY,
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
    payment_id INT IDENTITY(1,1) PRIMARY KEY,
    contract_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    payment_date DATE NOT NULL,
    FOREIGN KEY (contract_id) REFERENCES Contract (contract_id)
);

-- One-to-one: contract_id is UNIQUE, so a contract has at most one review.
CREATE TABLE Review (
    review_id INT IDENTITY(1,1) PRIMARY KEY,
    contract_id INT NOT NULL UNIQUE,
    student_id INT NOT NULL,
    client_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment NVARCHAR(MAX) NULL,
    FOREIGN KEY (contract_id) REFERENCES Contract (contract_id),
    FOREIGN KEY (student_id) REFERENCES Student (student_id),
    FOREIGN KEY (client_id) REFERENCES Client (client_id)
);
