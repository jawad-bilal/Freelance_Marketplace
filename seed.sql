-- Sample rows so every table has something to show.
-- The ids are written out on purpose, so the foreign keys are easy to read.
-- For example, Proposal 1 belongs to Project 1 and Student 1.

INSERT INTO Student (student_id, full_name, email, university, bio) VALUES
    (1, 'Ayesha Khan', 'ayesha@student.edu', 'City University', 'Builds small websites with HTML, CSS, and Python.'),
    (2, 'Bilal Ahmed', 'bilal@student.edu', 'City University', 'Designs logos and posters.'),
    (3, 'Sara Malik', 'sara@student.edu', 'National University', 'Writes articles and short reports.'),
    (4, 'Omar Farooq', 'omar@student.edu', 'National University', 'Cleans spreadsheets and writes small Python scripts.');

INSERT INTO Skill (skill_id, skill_name) VALUES
    (1, 'Web Development'),
    (2, 'Graphic Design'),
    (3, 'Content Writing'),
    (4, 'Data Entry'),
    (5, 'Python');

INSERT INTO StudentSkill (student_id, skill_id) VALUES
    (1, 1),
    (1, 5),
    (2, 2),
    (3, 3),
    (4, 4),
    (4, 5);

INSERT INTO Client (client_id, full_name, email, company) VALUES
    (1, 'Hina Raza', 'hina@brightmedia.com', 'Bright Media'),
    (2, 'Usman Ali', 'usman@localshop.com', 'Local Shop'),
    (3, 'Nadia Qureshi', 'nadia@campusnews.com', 'Campus News');

INSERT INTO Project (project_id, client_id, title, description, budget, status) VALUES
    (1, 1, 'University club website', 'A simple website with a home page, events page, and contact page.', 300.00, 'completed'),
    (2, 2, 'Shop logo', 'A logo that can be used on a sign and on Instagram.', 80.00, 'in_progress'),
    (3, 3, 'Welcome article', 'A short article for students who have just joined the university.', 50.00, 'open'),
    (4, 2, 'Clean a sales spreadsheet', 'Fix dates and remove duplicate rows in last months sales file.', 40.00, 'open');

INSERT INTO Proposal (proposal_id, project_id, student_id, cover_letter, bid_amount, status) VALUES
    (1, 1, 1, 'I can build the club website with HTML and CSS.', 280.00, 'accepted'),
    (2, 1, 4, 'I can assemble the pages and check the links.', 250.00, 'rejected'),
    (3, 2, 2, 'I will design two logo options and send the image files.', 75.00, 'accepted'),
    (4, 3, 3, 'I can write a clear 500 word welcome article.', 45.00, 'pending'),
    (5, 4, 4, 'I can clean the sheet and list the rows I removed.', 35.00, 'pending'),
    (6, 3, 1, 'I can edit the article and format it for the site.', 48.00, 'pending');

INSERT INTO Contract (contract_id, project_id, proposal_id, student_id, client_id, agreed_amount, start_date, status) VALUES
    (1, 1, 1, 1, 1, 280.00, '2026-09-01', 'completed'),
    (2, 2, 3, 2, 2, 75.00, '2026-10-01', 'active');

INSERT INTO Payment (payment_id, contract_id, amount, payment_date) VALUES
    (1, 1, 280.00, '2026-09-15'),
    (2, 2, 40.00, '2026-10-10');

INSERT INTO Review (review_id, contract_id, student_id, client_id, rating, comment) VALUES
    (1, 1, 1, 1, 5, 'The website was delivered on time and the pages are easy to update.');

-- The inserts above chose the ids. Move each counter forward so the
-- next row added from the website does not reuse id 1.
SELECT setval(pg_get_serial_sequence('student', 'student_id'), (SELECT MAX(student_id) FROM student));
SELECT setval(pg_get_serial_sequence('skill', 'skill_id'), (SELECT MAX(skill_id) FROM skill));
SELECT setval(pg_get_serial_sequence('client', 'client_id'), (SELECT MAX(client_id) FROM client));
SELECT setval(pg_get_serial_sequence('project', 'project_id'), (SELECT MAX(project_id) FROM project));
SELECT setval(pg_get_serial_sequence('proposal', 'proposal_id'), (SELECT MAX(proposal_id) FROM proposal));
SELECT setval(pg_get_serial_sequence('contract', 'contract_id'), (SELECT MAX(contract_id) FROM contract));
SELECT setval(pg_get_serial_sequence('payment', 'payment_id'), (SELECT MAX(payment_id) FROM payment));
SELECT setval(pg_get_serial_sequence('review', 'review_id'), (SELECT MAX(review_id) FROM review));
