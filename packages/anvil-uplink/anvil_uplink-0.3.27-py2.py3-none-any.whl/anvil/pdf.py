import anvil.server

#xx defFunction(anvil.pdf,%anvil.Media instance, component)!2: "Convert an Anvil component into a PDF. Returns an Anvil Media object." ["component_to_pdf"]
def form_to_pdf(*args, **kwargs):
    return anvil.server.call("anvil.private.pdf.component_to_pdf", {}, args, kwargs)


class PdfRenderer(object):
    def __init__(self, **kwargs):
        self.options = kwargs

    def render_form(self, *args, **kwargs):
        return anvil.server.call("anvil.private.pdf.component_to_pdf", self.options, args, kwargs)
