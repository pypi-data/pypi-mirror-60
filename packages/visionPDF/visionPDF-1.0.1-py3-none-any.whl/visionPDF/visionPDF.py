import PyPDF2
from karkipytranslator import PYTRANSLATOR
from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import letter, A4,landscape
from reportlab.lib import colors


class PDFReader:
    '''
    # Classe Responsavel pela leitura e manipulação de Arquivos PDF.
    #
    # USO:
    # 
    # >> reader = PDFReader(arquivo.pdf)  # Objeto Reader Criado e Pronto.
    # >> reader.numpages                  # Número de Páginas do Arquivo.
    # >> reader.file                      # Arquivo que Está sendo Usado.
    # >> reader.get_text(page)            # Retorna o texto da Página.
    # --------- OU -----------
    # >> reader.get_text()                # Retorna Todo o Texto do Documento.
    # 
    #              
    '''
    def __init__(self, file):
        self.file = file
        self._pdfReader = PyPDF2.PdfFileReader(open(self.file,'rb'))
        self._pdfWriter = PyPDF2.PdfFileWriter()
        self.numpages = self._pdfReader.numPages
        self.isEncrypted = self._pdfReader.isEncrypted

    def page(self,page):
        '''
        Retorna a página selecionada.
        '''
        return self._pdfReader.getPage(page)
        
    def get_text(self, page:int=None):
        '''
        # Função que retorna o Texto do documento:
        # ------ USO -------#
        #
        # get_text(numPage) -> Retorna o texto da pagina;
        #
        # ------- OU -------#
        #
        # get_text() -> Retorna todo o texto do Documento;
        #
        '''
        if page:
            return self._pdfReader.getPage(page).extractText()
        else:
            pages = ''
            for n in range(0, self.numpages):
                pages += self._pdfReader.getPage(n).extractText()
            return pages
    
    
    def info(self):
        '''
        Retorna Informações sobre o documento PDF.
        '''
        info = self._pdfReader.getDocumentInfo()
        
        obj_info = {}
        for dict_info in info:
            obj_info['{}'.format(dict_info[1:])] = info[dict_info]
        
        return obj_info
            

    def get_fields(self):
        '''
        Extrai os dados do campo se este PDF contiver campos de formulário interativos.
        '''
        return self._pdfReader.getFields(fileobj=self.file)
    
    def get_forms_fields(self):
        '''
        Recupera campos de formulário do documento com dados de texto (entradas, listas suspensas).
        '''
        return self._pdfReader.getFormTextFields()
    
    def get_destinations(self):
        '''
        Recupera os destinos nomeados presentes no documento.
        '''
        return self._pdfReader.getNamedDestinations()
    
    def get_page_layout(self):
        '''
        Retorna o layout da pagina em uso.
    
        '''
        return self._pdfReader.pageLayout
    def get_page_mode(self):
        '''
        Retorna o modo da página em uso.
        '''
        return self._pdfReader.pageMode
        
    
class PDFTranslate:
    '''
    # Classe Responsável pela Tradução de Textos
    # USO:
    # >> obj_trans = PDFTranslate(to_lang)    # to_lang -> Para qual linguagem quer traduzir . Ex: pt, en, kr, ...
    # >> traduzido_text = obj_trans.translate(text)            # text -> Objeto texto a ser traduzido.
                                                                retorna o texto traduzido.
    
    '''
    def __init__(self,to_lang:str):
        self.to_lang = to_lang
        self.lang = PYTRANSLATOR(self.to_lang)

    def translate(self,text:str):
        '''
        Método Responsável pela tradução.
        '''
        self.text = text
        return self.lang.translate(self.text)


class PDFWriter:
    '''
    # Classe Responsável por Criar Documentos PDF.
    # Uso:
    # >> writer = PDFWriter(file_out, orientation)    # file_out -> Arquivo PDF de saida.
    #                                                 # orientation -> Tipo de Orientação do Documento. Ex: portrait/landscape.
    # >> writer.addText(*args)                        # Adiciona texto ao Documento.
    # >> writer.addImage(*args)                       # Adiciona Imagem ao Documento.
    # >> ...
    '''
    def __init__(self,file_out:str,orientation:str=None):
        if not orientation or orientation == 'portrait':
            self.writer_pdf = canvas.Canvas(file_out,pagesize=letter)
        elif orientation == 'landscape':
            self.writer_pdf = canvas.Canvas(file_out,pagesize=landscape(letter))
        else:
            raise AttributeError('Orientação do PDF Invalida. USE: portrait/landscape')
    def page(self):
        '''
        Retorna o número da pagina em uso.
        '''
        return self.writer_pdf.getPageNumber()
    def addFont(self, font):
        '''
        Adiciona Fonte ao documento ou pagina em uso.
        
        Ex:
        Courier:
        Courier-Bold:
        Courier-BoldOblique:
        Courier-Oblique:
        Helvetica:
        Helvetica-Bold:
        Helvetica-BoldOblique:
        Helvetica-Oblique:
        Symbol:
        Times-Bold:
        Times-BoldItalic:
        Times-Italic:
        Times-Roman:
        ZapfDingbats:

        '''
        self.writer_pdf.setFont(font,16)

    def addFontSize(self, size):
        '''
        Adiciona Tamanho a letra do documento ou pagina em uso.
        '''
        self.writer_pdf.setFontSize(size)

    def addColor(self,color):
        '''
        Adiciona Cor ao Documento ou pagina em uso.
        USO:
        #ff0000 -> RED
        #00ff00 -> GREEN
        #0000ff -> BLUE
        ...
        '''
        self.writer_pdf.setFillColor(colors.HexColor(color))

    def addText(self,text,cordX,cordY, font:str=None, size_letter:str=None,color:str=None):
        '''
        Adiciona Texto a pagina em uso.
        Obs: Color -> HEX -> #00ff00
        '''
        if color:
            self.writer_pdf.setFillColor(colors.HexColor(color))
        if font and not size_letter:
            
            self.writer_pdf.setFont(font,16)
        elif font and size_letter:
            
            self.writer_pdf.setFont(font,size_letter)
        elif font and size_letter and color:
            
            self.writer_pdf.setFont(font,size_letter)
            self.writer_pdf.setFillColor(colors.HexColor(color))
        elif not color:
            self.writer_pdf.setFillColor(colors.black)
        self.writer_pdf.drawString(cordX,cordY,text)
        
    def addImage(self,image,cordX,cordY,width,height):
        '''
        Adiciona Imagens a pagina em uso
        '''
        self.writer_pdf.drawImage(image,cordX,cordY,width=width,height=height)

    def addCircle(self, cordX,cordY, radius, color=None):
        '''
        Adiciona Circulos a pagina em uso.
        '''
        if color:
            self.writer_pdf.setFillColor(colors.HexColor(color))
            self.writer_pdf.circle(cordX,cordY,radius,stroke=0,fill=1)
        else:
            self.writer_pdf.circle(cordX,cordY,radius,stroke=1)
    
    def addRectangle(self,cordX,cordY,width,height,color:str=None,radius:str=None):
        '''
        Adiciona Retangulos a pagina em uso.
        '''
        if color and radius:
            self.addColor(color)
            self.writer_pdf.roundRect(cordX,cordY,width,height,radius,stroke=0,fill=1)
        elif radius and not color:
            self.writer_pdf.roundRect(cordX,cordY,width,height,radius,stroke=1,fill=0)
        elif color and not radius:
            self.addColor(color)
            self.writer_pdf.roundRect(cordX,cordY,width,height,0,stroke=0,fill=1)
        else:
            self.writer_pdf.roundRect(cordX,cordY,width,height,0,stroke=1,fill=0)
    def save_page(self):
        '''
        Salva e fecha a pagina em uso.
        '''
        self.writer_pdf.showPage()

    
    def close(self):
        '''
        Salva o Documento PDF e Cria o Arquivo.
        '''
        self.writer_pdf.save()
        

if __name__ == '__main__':



    pdfW = PDFWriter('teste.pdf')
    pdfW.addText('ola teste', 300, 400,font='Courier',size_letter=50)
    pdfW.addText('pagina 1', 500, 500, font='Helvetica',size_letter=34)
    pdfW.addText('Outro texto', 200, 600, font='Times-Italic',size_letter=30, color='#ffab5f')
    pdfW.save_page()
    pdfW.addText('Pagina 2', 300,300,font='Helvetica-Bold', size_letter= 39, color='#bbff56')
    pdfW.save_page()
    pdfW.addText('Pagina 3', 100, 100)
    pdfW.addImage('foto.jpg',300,200,200,200)
    pdfW.addCircle(400,500,30,color='#ff8945')
    pdfW.addRectangle(200,300,200,200,radius=3)
    pdfW.save_page()
    pdfW.close()
    
    

    
    
    




