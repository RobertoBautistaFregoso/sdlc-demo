-- S1: initial students table for onboarding state persistence.
create table students (
    whatsapp_number    text        primary key,
    onboarding_state   text        not null,
    student_first_name text,
    exam_date          date,
    consent_text       text,
    consent_at         timestamptz,
    created_at         timestamptz not null default now(),
    updated_at         timestamptz not null default now()
);

create index students_updated_at_idx on students (updated_at);
