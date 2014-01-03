from django.template import Template, Context
from django.test import TestCase

TITLE = '<h4>title</h4>'
BODY = '<p>body</p>'
FOOTER = '<small>footer</small>'


class PanelTagTests(TestCase):
    def test_simple_tag(self):
        t = Template("""
            {%% load categories %%}
            {%% panel %%}%s{%% endpanel %%}
            """ % TITLE)
        rendered_text = t.render(Context())
        self.assertIn(TITLE, rendered_text)

    def test_tag_with_body(self):
        t = Template("""
            {%% load categories %%}
            {%% panel %%}%s{%% body %%}%s{%% endpanel %%}
            """ % (TITLE, BODY))
        rendered_text = t.render(Context())
        self.assertIn(TITLE, rendered_text)
        self.assertIn(BODY, rendered_text)

    def test_tag_with_footer(self):
        t = Template("""
            {%% load categories %%}
            {%% panel %%}%s{%% footer %%}%s{%% endpanel %%}
            """ % (TITLE, FOOTER))
        rendered_text = t.render(Context())
        self.assertIn(TITLE, rendered_text)
        self.assertIn(FOOTER, rendered_text)

    def test_tag_with_body_and_footer(self):
        t = Template("""
            {%% load categories %%}
            {%% panel %%}%s{%% body %%}%s{%% footer %%}%s{%% endpanel %%}
            """ % (TITLE, BODY, FOOTER))
        rendered_text = t.render(Context())
        self.assertIn(TITLE, rendered_text)
        self.assertIn(BODY, rendered_text)
        self.assertIn(FOOTER, rendered_text)

    def test_modal_dialog(self):
        t = Template("""
            {%% load categories %%}
            {%% panel True%%}%s{%% body %%}%s{%% footer %%}%s{%% endpanel %%}
            """ % (TITLE, BODY, FOOTER))
        rendered_text = t.render(Context())
        self.assertIn(TITLE, rendered_text)
        self.assertIn(BODY, rendered_text)
        self.assertIn(FOOTER, rendered_text)

    def test_non_modal_dialog(self):
        t = Template("""
            {%% load categories %%}
            {%% panel False%%}%s{%% body %%}%s{%% footer %%}%s{%% endpanel %%}
            """ % (TITLE, BODY, FOOTER))
        rendered_text = t.render(Context())
        self.assertNotIn(TITLE, rendered_text)
        self.assertIn(BODY, rendered_text)
        self.assertIn(FOOTER, rendered_text)

    def test_non_modal_dialog_with_non_defined_parameter(self):
        t = Template("""
            {%% load categories %%}
            {%% panel is_modal%%}%s{%% body %%}%s{%% footer %%}%s{%% endpanel %%}
            """ % (TITLE, BODY, FOOTER))
        rendered_text = t.render(Context())
        self.assertIn(TITLE, rendered_text)
        self.assertIn(BODY, rendered_text)
        self.assertIn(FOOTER, rendered_text)
