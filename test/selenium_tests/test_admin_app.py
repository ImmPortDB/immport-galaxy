from .framework import (
    selenium_test,
    SeleniumTestCase,
)


class AdminAppTestCase(SeleniumTestCase):

    requires_admin = True

    @selenium_test
    def test_admin_server_display(self):
        admin_component = self.components.admin
        self.admin_login()
        self.admin_open()
        self.screenshot("admin_landing")
        admin_component.index.datatypes.wait_for_and_click()
        with self.main_panel():
            admin_component.datatypes_grid.wait_for_visible()
        self.screenshot("admin_datatypes")

        admin_component.index.data_tables.wait_for_and_click()
        admin_component.data_tables_grid.wait_for_visible()
        self.screenshot("admin_data_tables")

        admin_component.index.display_applications.wait_for_and_click()
        with self.main_panel():
            admin_component.display_applications_grid.wait_for_visible()
        self.screenshot("admin_display_applications")

        admin_component.index.jobs.wait_for_and_click()
        with self.main_panel():
            admin_component.update_jobs.wait_for_visible()
        self.screenshot("admin_manage_jobs")

        admin_component.index.local_data.wait_for_and_click()
        with self.main_panel():
            title_element = admin_component.data_managers_title.wait_for_visible()
            assert title_element.text == "Data Manager"
        self.screenshot("admin_local_data")

    @selenium_test
    def test_admin_user_display(self):
        admin_component = self.components.admin
        self.admin_login()
        self.admin_open()

        admin_component.index.users.wait_for_and_click()
        admin_component.users_grid.wait_for_visible()
        self.screenshot("admin_users")
        admin_component.users_grid_create_button.wait_for_and_click()
        admin_component.registration_form.wait_for_visible()
        self.screenshot("admin_user_registration")

        self.admin_open()
        admin_component.index.groups.wait_for_and_click()
        admin_component.groups_grid.wait_for_visible()
        self.screenshot("admin_groups")

        admin_component.groups_grid_create_button.wait_for_and_click()
        admin_component.groups_create_view.wait_for_visible()
        self.screenshot("admin_groups_create")

        self.admin_open()
        admin_component.index.roles.wait_for_and_click()
        admin_component.roles_grid.wait_for_visible()
        self.screenshot("admin_roles")
