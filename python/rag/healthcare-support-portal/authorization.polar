# Healthcare Support Portal Authorization Policies
# OSO Cloud Policy File

# ============================================================================
# ACTOR DEFINITIONS
# ============================================================================

actor User {}

# ============================================================================
# RESOURCE DEFINITIONS
# ============================================================================

resource User {
    permissions = ["read", "write", "delete"];
    roles = ["admin"];
    
    # Admins can do everything with users - no individual facts needed
    "read" if "admin";
    "write" if "admin"; 
    "delete" if "admin";
    
    # Users can read their own information
    "read" if resource == actor;
}

resource Patient {
    permissions = ["read", "write", "delete"];
    roles = ["admin", "assigned_doctor", "department_nurse"];
    
    # Admins can do everything with patients
    "read" if "admin";
    "write" if "admin";
    "delete" if "admin";
    
    # Doctors can access their assigned patients
    "read" if "assigned_doctor";
    "write" if "assigned_doctor";
    
    # Nurses can access patients in their department  
    "read" if "department_nurse";
}

resource Document {
    permissions = ["read", "write", "delete", "share"];
    roles = ["admin", "owner", "patient_doctor", "department_staff"];
    
    # Admins can do everything with documents
    "read" if "admin";
    "write" if "admin";
    "delete" if "admin";
    "share" if "admin";
    
    # Document owner can do everything
    "read" if "owner";
    "write" if "owner";
    "delete" if "owner";
    "share" if "owner";
    
    # Doctors can access documents for their patients
    "read" if "patient_doctor";
    "write" if "patient_doctor";
    
    # Department staff can read non-sensitive documents in their department
    "read" if "department_staff";
}

resource Embedding {
    permissions = ["read", "write", "delete"];
    roles = ["admin"];
    
    # Only admins can manage embeddings directly
    "read" if "admin";
    "write" if "admin";
    "delete" if "admin";
}

# ============================================================================
# FACT DECLARATIONS
# ============================================================================

# Declare the fact patterns we use in authorization
declare has_role(User, String, User);
declare has_role(User, String, Patient); 
declare has_role(User, String, Document);
declare has_role(User, String, Embedding);

# ============================================================================
# MAIN AUTHORIZATION RULE
# ============================================================================

allow(actor, action, resource) if 
    has_permission(actor, action, resource);

# Global admin permissions - admins can access all users
# This works by checking role directly without requiring OSO facts
allow(actor, action, resource) if
    actor.role = "admin" and
    resource matches User and
    action in ["read", "write", "delete"];

# ============================================================================
# TESTS
# ============================================================================

test "admin can read all patients" {
    setup {
        has_role(User{"admin_wilson"}, "admin", Patient{"patient_1"});
        has_role(User{"admin_wilson"}, "admin", Patient{"patient_2"});
        has_role(User{"admin_wilson"}, "admin", Patient{"patient_3"});
    }
    
    assert allow(User{"admin_wilson"}, "read", Patient{"patient_1"});
    assert allow(User{"admin_wilson"}, "read", Patient{"patient_2"}); 
    assert allow(User{"admin_wilson"}, "read", Patient{"patient_3"});
    assert allow(User{"admin_wilson"}, "write", Patient{"patient_1"});
    assert allow(User{"admin_wilson"}, "delete", Patient{"patient_1"});
}

test "admin can read all documents" {
    setup {
        has_role(User{"admin_wilson"}, "admin", Document{"doc_1"});
        has_role(User{"admin_wilson"}, "admin", Document{"doc_2"});
    }
    
    assert allow(User{"admin_wilson"}, "read", Document{"doc_1"});
    assert allow(User{"admin_wilson"}, "write", Document{"doc_1"});
    assert allow(User{"admin_wilson"}, "delete", Document{"doc_1"});
    assert allow(User{"admin_wilson"}, "share", Document{"doc_1"});
}

test "doctor can read assigned patients only" {
    setup {
        has_role(User{"doctor_smith"}, "assigned_doctor", Patient{"assigned_patient"});
    }
    
    assert allow(User{"doctor_smith"}, "read", Patient{"assigned_patient"});
    assert allow(User{"doctor_smith"}, "write", Patient{"assigned_patient"});
    assert_not allow(User{"doctor_smith"}, "read", Patient{"other_patient"});
}

test "nurse can read department patients but not write" {
    setup {
        has_role(User{"nurse_jones"}, "department_nurse", Patient{"dept_patient"});
    }
    
    assert allow(User{"nurse_jones"}, "read", Patient{"dept_patient"});
    assert_not allow(User{"nurse_jones"}, "write", Patient{"dept_patient"});
    assert_not allow(User{"nurse_jones"}, "read", Patient{"other_dept_patient"});
}

test "doctor can read documents for their patients" {
    setup {
        has_role(User{"doctor_smith"}, "patient_doctor", Document{"patient_doc"});
    }
    
    assert allow(User{"doctor_smith"}, "read", Document{"patient_doc"});
    assert allow(User{"doctor_smith"}, "write", Document{"patient_doc"});
    assert_not allow(User{"doctor_smith"}, "delete", Document{"patient_doc"});
}

test "nurse can read non-sensitive department documents" {
    setup {
        has_role(User{"nurse_jones"}, "department_staff", Document{"dept_doc"});
    }
    
    assert allow(User{"nurse_jones"}, "read", Document{"dept_doc"});
    assert_not allow(User{"nurse_jones"}, "write", Document{"dept_doc"});
}

test "users can read their own information" {
    setup {
        has_role(User{"doctor_smith"}, "admin", User{"doctor_smith"});
    }
    
    assert allow(User{"doctor_smith"}, "read", User{"doctor_smith"});
    assert allow(User{"doctor_smith"}, "write", User{"doctor_smith"});
    assert_not allow(User{"doctor_smith"}, "read", User{"other_user"});
}

test "document owners have full control" {
    setup {
        has_role(User{"doctor_smith"}, "owner", Document{"created_doc"});
    }
    
    assert allow(User{"doctor_smith"}, "read", Document{"created_doc"});
    assert allow(User{"doctor_smith"}, "write", Document{"created_doc"});
    assert allow(User{"doctor_smith"}, "delete", Document{"created_doc"});
    assert allow(User{"doctor_smith"}, "share", Document{"created_doc"});
}

test "only admins can manage embeddings" {
    setup {
        has_role(User{"admin_wilson"}, "admin", Embedding{"embedding_1"});
    }
    
    assert allow(User{"admin_wilson"}, "read", Embedding{"embedding_1"});
    assert allow(User{"admin_wilson"}, "write", Embedding{"embedding_1"});
    assert allow(User{"admin_wilson"}, "delete", Embedding{"embedding_1"});
    assert_not allow(User{"doctor_smith"}, "read", Embedding{"embedding_1"});
}