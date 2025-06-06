sql_commands = ['''
CREATE TABLE Courts (
    CourtID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    CourtName VARCHAR(255) NOT NULL UNIQUE,
    Jurisdiction VARCHAR(255),
    Address VARCHAR(255)
);
''', 

'''
CREATE TABLE CaseTypes (
    CaseTypeID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    TypeName VARCHAR(100) NOT NULL UNIQUE
);
''',

'''
CREATE TABLE CaseStatuses (
    StatusID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    StatusName VARCHAR(100) NOT NULL UNIQUE
);
''',

'''
CREATE TABLE Specializations (
    SpecializationID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    SpecializationName VARCHAR(100) NOT NULL UNIQUE
);
''',

'''
CREATE TABLE DocumentTypes (
    DocumentTypeID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    TypeName VARCHAR(100) NOT NULL UNIQUE
);
''',

'''
CREATE TABLE Cases (
    CaseID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    CaseNumber VARCHAR(255) NOT NULL UNIQUE,
    CaseName VARCHAR(255),
    CourtID INT,
    CaseTypeID INT,
    DateFiled DATE,
    DateClosed DATE NULL,
    StatusID INT,
    Description TEXT NULL,
    FOREIGN KEY (CourtID) REFERENCES Courts(CourtID),
    FOREIGN KEY (CaseTypeID) REFERENCES CaseTypes(CaseTypeID),
    FOREIGN KEY (StatusID) REFERENCES CaseStatuses(StatusID)
);
''',

'''
CREATE TABLE Clients (
    ClientID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    ContactNumber VARCHAR(50),
    Email VARCHAR(255) UNIQUE,
    Address VARCHAR(255)
);
''',

'''
CREATE TABLE Lawyers (
    LawyerID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    BarNumber VARCHAR(100) UNIQUE,
    SpecializationID INT,
    ContactNumber VARCHAR(50),
    Email VARCHAR(255) UNIQUE,
    FOREIGN KEY (SpecializationID) REFERENCES Specializations(SpecializationID)
);
''',

'''
CREATE TABLE CaseClients (
    CaseClientID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    CaseID INT,
    ClientID INT,
    RoleInCase VARCHAR(100),
    FOREIGN KEY (CaseID) REFERENCES Cases(CaseID),
    FOREIGN KEY (ClientID) REFERENCES Clients(ClientID)
);
''',

'''
CREATE TABLE CaseLawyers (
    CaseLawyerID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    CaseID INT,
    LawyerID INT,
    RoleInCase VARCHAR(100),
    FOREIGN KEY (CaseID) REFERENCES Cases(CaseID),
    FOREIGN KEY (LawyerID) REFERENCES Lawyers(LawyerID)
);
''',

'''
CREATE TABLE Documents (
    DocumentID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    CaseID INT,
    DocumentTypeID INT,
    DocumentName VARCHAR(255) NOT NULL,
    FilePath VARCHAR(255) NOT NULL,
    DateCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CaseID) REFERENCES Cases(CaseID),
    FOREIGN KEY (DocumentTypeID) REFERENCES DocumentTypes(DocumentTypeID)
);
''',

'''
CREATE TABLE Hearings (
    HearingID INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    CaseID INT,
    HearingDate TIMESTAMP NOT NULL,
    Courtroom VARCHAR(100) NULL,
    Notes TEXT NULL,
    FOREIGN KEY (CaseID) REFERENCES Cases(CaseID)
);
''',

'''
CREATE INDEX idx_cases_courtid ON Cases (CourtID);
''',
'''
CREATE INDEX idx_cases_casetypeid ON Cases (CaseTypeID);
''',
'''
CREATE INDEX idx_cases_statusid ON Cases (StatusID);
''',
'''
CREATE INDEX idx_lawyers_specializationid ON Lawyers (SpecializationID);

''',
'''
CREATE INDEX idx_caseclients_caseid ON CaseClients (CaseID);

''',
'''
CREATE INDEX idx_caseclients_clientid ON CaseClients (ClientID);

''',
'''
CREATE INDEX idx_caselawyers_caseid ON CaseLawyers (CaseID);

''',
'''
CREATE INDEX idx_caselawyers_lawyerid ON CaseLawyers (LawyerID);

''',
'''
CREATE INDEX idx_documents_caseid ON Documents (CaseID);

''',
'''
CREATE INDEX idx_documents_doctypeid ON Documents (DocumentTypeID);

''',
'''
CREATE INDEX idx_hearings_caseid ON Hearings (CaseID);
''',

'''
INSERT INTO Courts (CourtName, Jurisdiction, Address) VALUES
('Supreme Court of ExampleLand', 'National', '1 High Street, Capital City, EL 10001'),
('District Court of North County', 'North County', '123 Main Avenue, Northville, EL 20304'),
('Appellate Court - First Circuit', 'First Circuit Appeals', '45 West End Road, Metro City, EL 30506'),
('Small Claims Court of Rivertown', 'Rivertown Area', '7 River Bend, Rivertown, EL 40708');
''',

'''
INSERT INTO CaseTypes (TypeName) VALUES
('Civil Litigation'),
('Criminal Defense'),
('Corporate Law'),
('Family Law'),
('Administrative Law'),
('Personal Injury'),
('Real Estate Law');
''',

'''
INSERT INTO CaseStatuses (StatusName) VALUES
('Filed'),
('In Progress'),
('Discovery'),
('Awaiting Hearing'),
('Awaiting Judgment'),
('Appealed'),
('Closed - Won'),
('Closed - Lost'),
('Closed - Settled'),
('Dismissed');
''',

'''

INSERT INTO Specializations (SpecializationName) VALUES
('Criminal Law'),
('Corporate Law'),
('Family Law'),
('Civil Litigation'),
('Real Estate'),
('Intellectual Property'),
('Medical Malpractice');
''',

'''
INSERT INTO DocumentTypes (TypeName) VALUES
('Complaint'),
('Summons'),
('Motion'),
('Affidavit'),
('Court Order'),
('Judgment'),
('Discovery Request'),
('Pleading'),
('Evidence File'),
('Settlement Agreement');
''',

'''
INSERT INTO Clients (FirstName, LastName, ContactNumber, Email, Address) VALUES
('John', 'Smith', '555-0101', 'john.smith@example.com', '123 Oak Lane, Springfield, EL 60602'),
('Alice', 'Johnson', '555-0102', 'alice.johnson@example.net', '456 Pine Street, Metropolis, EL 70703'),
('Robert', 'Williams', '555-0103', 'rob.williams@example.org', '789 Birch Road, Gotham, EL 80804'),
('Emily', 'Brown', '555-0104', 'emily.brown@example.com', '101 Maple Drive, Star City, EL 90905'),
('Michael', 'Jones', '555-0105', 'michael.jones@example.net', '234 Cedar Avenue, Central City, EL 10106');
''',

'''
INSERT INTO Lawyers (FirstName, LastName, BarNumber, SpecializationID, ContactNumber, Email) VALUES
('Laura', 'Davis', 'BAR001', 1, '555-0201', 'laura.davis@lawfirm.com'),
('James', 'Miller', 'BAR002', 2, '555-0202', 'james.miller@lawfirm.net'),
('Sarah', 'Wilson', 'BAR003', 3, '555-0203', 'sarah.wilson@lawfirm.org'),
('David', 'Garcia', 'BAR004', 4, '555-0204', 'david.garcia@lawfirm.com'),
('Jessica', 'Rodriguez', 'BAR005', 5, '555-0205', 'jessica.rodriguez@lawfirm.net');
''',

'''
INSERT INTO Cases (CaseNumber, CaseName, CourtID, CaseTypeID, DateFiled, DateClosed, StatusID, Description) VALUES
('CVL-2023-001', 'Smith v. Johnson Construction', 2, 1, '2023-03-15', NULL, 2, 'Dispute over construction contract terms and payment.'),
('CRM-2024-002', 'State v. Williams', 2, 2, '2024-01-20', NULL, 3, 'Criminal defense for alleged theft.'),
('CORP-2023-003', 'Brown Innovations Merger', 1, 3, '2023-07-01', '2024-02-10', 7, 'Merger and acquisition of Brown Innovations by Global Corp.'),
('FAM-2024-004', 'Jones v. Jones Divorce', 4, 4, '2024-04-05', NULL, 2, 'Divorce proceedings and child custody dispute.'),
('PI-2023-005', 'Smith v. Transit Co.', 2, 6, '2023-11-10', NULL, 4, 'Personal injury claim resulting from a public transport accident.');

''',

'''
INSERT INTO CaseClients (CaseID, ClientID, RoleInCase) VALUES
(1, 1, 'Plaintiff'),
(1, 2, 'Defendant (Representative)'),
(2, 3, 'Defendant'),
(3, 4, 'Acquiring Party'),
(4, 5, 'Petitioner'),
(4, 1, 'Respondent'),
(5, 1, 'Claimant');
''',
'''
INSERT INTO CaseLawyers (CaseID, LawyerID, RoleInCase) VALUES
(1, 4, 'Plaintiff''s Counsel'),
(1, 2, 'Defense Counsel'),
(2, 1, 'Defense Counsel'),
(3, 2, 'Lead Counsel for Acquirer'),
(4, 3, 'Petitioner''s Counsel'),
(4, 5, 'Respondent''s Counsel'),
(5, 4, 'Claimant''s Counsel');
''',

'''
INSERT INTO Documents (CaseID, DocumentTypeID, DocumentName, FilePath, DateCreated) VALUES
(1, 1, 'Initial Complaint - Smith v Johnson', '/docs/cvl2023001/complaint.pdf', '2023-03-15 10:00:00'),
(1, 7, 'First Set of Interrogatories to Johnson Construction', '/docs/cvl2023001/interrogatories_set1.pdf', '2023-06-01 14:30:00'),
(2, 8, 'Plea of Not Guilty - Williams', '/docs/crm2024002/plea_not_guilty.pdf', '2024-01-25 09:15:00'),
(3, 10, 'Final Merger Agreement - Brown & Global', '/docs/corp2023003/merger_agreement_final.pdf', '2024-02-05 17:00:00'),
(4, 1, 'Divorce Petition - Jones v Jones', '/docs/fam2024004/divorce_petition.pdf', '2024-04-05 11:00:00'),
(5, 9, 'Accident Report - Smith PI', '/docs/pi2023005/accident_report.pdf', '2023-11-12 16:00:00');

''',

'''
INSERT INTO Hearings (CaseID, HearingDate, Courtroom, Notes) VALUES
(1, '2023-09-05 10:00:00', 'Courtroom 3B', 'Initial hearing, scheduling order discussed.'),
(2, '2024-05-15 14:00:00', 'Courtroom 1A', 'Bail hearing for Mr. Williams.'),
(4, '2024-07-22 09:30:00', 'Chambers 2', 'Mediation session for custody.'),
(5, '2024-06-10 11:00:00', 'Courtroom 2C', 'Hearing on motion for summary judgment.');

''']