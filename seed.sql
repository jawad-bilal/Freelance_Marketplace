-- Sample rows so every table has something to show.
-- The ids are written out on purpose, so the foreign keys are easy to read.
-- IDENTITY_INSERT lets us choose those ids on SQL Server.

SET IDENTITY_INSERT Student ON;
INSERT INTO Student (student_id, full_name, email, university, bio) VALUES
    (1, 'Ayesha Khan', 'ayesha@student.edu', 'City University', 'Builds small websites with HTML, CSS, and Python.'),
    (2, 'Bilal Ahmed', 'bilal@student.edu', 'City University', 'Designs logos and posters.'),
    (3, 'Sara Malik', 'sara@student.edu', 'National University', 'Writes articles and short reports.'),
    (4, 'Omar Farooq', 'omar@student.edu', 'National University', 'Cleans spreadsheets and writes small Python scripts.');
SET IDENTITY_INSERT Student OFF;

SET IDENTITY_INSERT Skill ON;
INSERT INTO Skill (skill_id, skill_name) VALUES
    (1, 'Web Development'),
    (2, 'Graphic Design'),
    (3, 'Content Writing'),
    (4, 'Data Entry'),
    (5, 'Python');
SET IDENTITY_INSERT Skill OFF;

INSERT INTO StudentSkill (student_id, skill_id) VALUES
    (1, 1),
    (1, 5),
    (2, 2),
    (3, 3),
    (4, 4),
    (4, 5);

SET IDENTITY_INSERT Client ON;
INSERT INTO Client (client_id, full_name, email, company) VALUES
    (1, 'Hina Raza', 'hina@brightmedia.com', 'Bright Media'),
    (2, 'Usman Ali', 'usman@localshop.com', 'Local Shop'),
    (3, 'Nadia Qureshi', 'nadia@campusnews.com', 'Campus News');
SET IDENTITY_INSERT Client OFF;

SET IDENTITY_INSERT Project ON;
INSERT INTO Project (project_id, client_id, title, description, budget, status) VALUES
    (1, 1, 'University club website', 'A simple website with a home page, events page, and contact page.', 300.00, 'completed'),
    (2, 2, 'Shop logo', 'A logo that can be used on a sign and on Instagram.', 80.00, 'in_progress'),
    (3, 3, 'Welcome article', 'A short article for students who have just joined the university.', 50.00, 'open'),
    (4, 2, 'Clean a sales spreadsheet', 'Fix dates and remove duplicate rows in last months sales file.', 40.00, 'open');
SET IDENTITY_INSERT Project OFF;

SET IDENTITY_INSERT Proposal ON;
INSERT INTO Proposal (proposal_id, project_id, student_id, cover_letter, bid_amount, status) VALUES
    (1, 1, 1, 'I can build the club website with HTML and CSS.', 280.00, 'accepted'),
    (2, 1, 4, 'I can assemble the pages and check the links.', 250.00, 'rejected'),
    (3, 2, 2, 'I will design two logo options and send the image files.', 75.00, 'accepted'),
    (4, 3, 3, 'I can write a clear 500 word welcome article.', 45.00, 'pending'),
    (5, 4, 4, 'I can clean the sheet and list the rows I removed.', 35.00, 'pending'),
    (6, 3, 1, 'I can edit the article and format it for the site.', 48.00, 'pending');
SET IDENTITY_INSERT Proposal OFF;

SET IDENTITY_INSERT Contract ON;
INSERT INTO Contract (contract_id, project_id, proposal_id, student_id, client_id, agreed_amount, start_date, status) VALUES
    (1, 1, 1, 1, 1, 280.00, '2026-09-01', 'completed'),
    (2, 2, 3, 2, 2, 75.00, '2026-10-01', 'active');
SET IDENTITY_INSERT Contract OFF;

SET IDENTITY_INSERT Payment ON;
INSERT INTO Payment (payment_id, contract_id, amount, payment_date) VALUES
    (1, 1, 280.00, '2026-09-15'),
    (2, 2, 40.00, '2026-10-10');
SET IDENTITY_INSERT Payment OFF;

SET IDENTITY_INSERT Review ON;
INSERT INTO Review (review_id, contract_id, student_id, client_id, rating, comment) VALUES
    (1, 1, 1, 1, 5, 'The website was delivered on time and the pages are easy to update.');
SET IDENTITY_INSERT Review OFF;

-- After choosing ids by hand, move the identity counters forward
-- so the next website insert does not reuse id 1.
DBCC CHECKIDENT ('Student', RESEED, 4);
DBCC CHECKIDENT ('Skill', RESEED, 5);
DBCC CHECKIDENT ('Client', RESEED, 3);
DBCC CHECKIDENT ('Project', RESEED, 4);
DBCC CHECKIDENT ('Proposal', RESEED, 6);
DBCC CHECKIDENT ('Contract', RESEED, 2);
DBCC CHECKIDENT ('Payment', RESEED, 2);
DBCC CHECKIDENT ('Review', RESEED, 1);
