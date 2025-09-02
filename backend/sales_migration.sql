-- Sales Module Database Migration
-- This creates all necessary tables for the Sales module

-- Create missing master tables if they don't exist

-- Create Account Sub Types table
CREATE TABLE IF NOT EXISTS mst_account_sub_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    created_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    updated_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Titles table
CREATE TABLE IF NOT EXISTS mst_titles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    created_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    updated_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Companies table
CREATE TABLE IF NOT EXISTS tbl_companies (
    id SERIAL PRIMARY KEY,
    gst_no VARCHAR(15),
    pan_no VARCHAR(10),
    industry_segment_id INTEGER REFERENCES mst_industry_segments(id),
    company_name VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    is_child BOOLEAN DEFAULT false,
    parent_company_id INTEGER REFERENCES tbl_companies(id),
    account_type_id INTEGER REFERENCES mst_account_types(id),
    account_sub_type_id INTEGER REFERENCES mst_account_sub_types(id),
    business_type_id INTEGER REFERENCES mst_business_types(id),
    account_region_id INTEGER REFERENCES mst_regions(id),
    company_profile TEXT,
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    created_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    updated_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Company Addresses table
CREATE TABLE IF NOT EXISTS tbl_company_addresses (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES tbl_companies(id) ON DELETE CASCADE,
    address_type_id INTEGER REFERENCES mst_address_types(id),
    address TEXT,
    country_id INTEGER REFERENCES mst_countries(id),
    state_id INTEGER REFERENCES mst_states(id),
    city_id INTEGER REFERENCES mst_cities(id),
    zip_code VARCHAR(10),
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    created_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    updated_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Company Turnover table
CREATE TABLE IF NOT EXISTS tbl_company_turnover (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES tbl_companies(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    revenue DECIMAL(15,2),
    currency_id INTEGER REFERENCES mst_currencies(id),
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    created_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    updated_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Company Profit table
CREATE TABLE IF NOT EXISTS tbl_company_profit (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES tbl_companies(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    revenue DECIMAL(15,2),
    currency_id INTEGER REFERENCES mst_currencies(id),
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    created_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    updated_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Company Documents table
CREATE TABLE IF NOT EXISTS tbl_company_documents (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES tbl_companies(id) ON DELETE CASCADE,
    document_type_id INTEGER REFERENCES mst_document_types(id),
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_size INTEGER,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    created_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    updated_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Contacts table
CREATE TABLE IF NOT EXISTS tbl_contacts (
    id SERIAL PRIMARY KEY,
    title_id INTEGER REFERENCES mst_titles(id),
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    dob DATE,
    company_id INTEGER NOT NULL REFERENCES tbl_companies(id) ON DELETE CASCADE,
    designation_id INTEGER REFERENCES mst_designations(id),
    email VARCHAR(150),
    fax VARCHAR(20),
    primary_no VARCHAR(15),
    secondary_no VARCHAR(15),
    alternate_no VARCHAR(15),
    dont_solicit BOOLEAN DEFAULT false,
    dont_mail BOOLEAN DEFAULT false,
    dont_fax BOOLEAN DEFAULT false,
    dont_email BOOLEAN DEFAULT false,
    dont_call BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    created_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    updated_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Contact Addresses table
CREATE TABLE IF NOT EXISTS tbl_contact_addresses (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES tbl_contacts(id) ON DELETE CASCADE,
    address_type_id INTEGER REFERENCES mst_address_types(id),
    address TEXT,
    country_id INTEGER REFERENCES mst_countries(id),
    state_id INTEGER REFERENCES mst_states(id),
    city_id INTEGER REFERENCES mst_cities(id),
    zip_code VARCHAR(10),
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    created_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    updated_by INTEGER REFERENCES tbl_users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Sales Module into modules table
INSERT INTO mst_modules (id, name, description, is_active, is_deleted, created_at, updated_at)
SELECT 2, 'SALES', 'Sales module for company and contact management', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM mst_modules WHERE id = 2);

-- Insert Sales parent menu
INSERT INTO mst_menus (id, name, path, parent_id, module_id, order_index, icon, is_sidebar, is_active, is_deleted, created_at, updated_at)
SELECT 100, 'SALES', null, null, 2, 2, 'fas fa-chart-line', true, true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM mst_menus WHERE id = 100);

-- Insert Companies menu
INSERT INTO mst_menus (id, name, path, parent_id, module_id, order_index, icon, is_sidebar, is_active, is_deleted, created_at, updated_at)
SELECT 101, 'Companies', '/sales/companies', 100, 2, 1, 'fas fa-building', true, true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM mst_menus WHERE id = 101);

-- Insert Contacts menu
INSERT INTO mst_menus (id, name, path, parent_id, module_id, order_index, icon, is_sidebar, is_active, is_deleted, created_at, updated_at)
SELECT 102, 'Contacts', '/sales/contacts', 100, 2, 2, 'fas fa-users', true, true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM mst_menus WHERE id = 102);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_companies_name ON tbl_companies(company_name);
CREATE INDEX IF NOT EXISTS idx_companies_gst ON tbl_companies(gst_no);
CREATE INDEX IF NOT EXISTS idx_companies_pan ON tbl_companies(pan_no);
CREATE INDEX IF NOT EXISTS idx_companies_active ON tbl_companies(is_active, is_deleted);
CREATE INDEX IF NOT EXISTS idx_contacts_company ON tbl_contacts(company_id);
CREATE INDEX IF NOT EXISTS idx_contacts_name ON tbl_contacts(first_name, last_name);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON tbl_contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_active ON tbl_contacts(is_active, is_deleted);

-- Insert some sample titles
INSERT INTO mst_titles (name, description, is_active, is_deleted, created_at, updated_at)
SELECT name, description, true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM (VALUES 
    ('Mr.', 'Mister'),
    ('Ms.', 'Miss'),
    ('Mrs.', 'Missus'),
    ('Dr.', 'Doctor'),
    ('Prof.', 'Professor')
) AS titles(name, description)
WHERE NOT EXISTS (SELECT 1 FROM mst_titles WHERE mst_titles.name = titles.name);

-- Insert some sample account sub types
INSERT INTO mst_account_sub_types (name, description, is_active, is_deleted, created_at, updated_at)
SELECT name, description, true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM (VALUES 
    ('Direct Client', 'Direct client relationship'),
    ('Partner Client', 'Client through partner'),
    ('Prospect', 'Potential client'),
    ('Lead', 'Sales lead')
) AS subtypes(name, description)
WHERE NOT EXISTS (SELECT 1 FROM mst_account_sub_types WHERE mst_account_sub_types.name = subtypes.name);