import flet as ft
from ui.requests_form import RequestsForm
from database import Database

# Mock DB and Page
class MockDB:
    pass

class MockPage:
    def update(self):
        pass
    snack_bar = None

def test_structure():
    print("--- Testing RequestsForm Structure ---")
    try:
        page = MockPage()
        db = MockDB()
        
        # Instantiate
        form = RequestsForm(page, db, 1, lambda _: None)
        
        # RequestsForm returns a Container -> Column -> (Row, Divider, Row, Column)
        # The inner Column has the form fields.
        
        main_col = form.content # Column
        content_area = main_col.controls[3] # Container
        inner_content = content_area.content # Column from get_application_form
        
        print(f"Inner Content Type: {type(inner_content)}")
        
        controls = inner_content.controls
        print(f"Number of controls in form: {len(controls)}")
        
        found_reason_template = False
        found_manual_input = False
        
        for c in controls:
            if isinstance(c, ft.Dropdown) and c.label == "理由・内容（選択）":
                found_reason_template = True
                print("Found Reason Template Dropdown")
            if isinstance(c, ft.TextField) and c.label == "理由・内容（詳細手入力）":
                found_manual_input = True
                print("Found Manual Input TextField")
                
        if found_reason_template and found_manual_input:
            print("SUCCESS: New UI components detected.")
        else:
            print("FAILURE: New UI components NOT detected.")
            print([c.label for c in controls if hasattr(c, "label")])

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_structure()
