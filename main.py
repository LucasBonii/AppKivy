from kivy.app import App
from kivy.lang import Builder
import requests
from telas import *
from botoes import *
from bannervenda import BannerVenda
from bannervendedor import BannerVendedor
from myfirebase import MyFireBase
import os
from datetime import date
from functools import partial

#001824 #001024 #006D7E #032640



GUI = Builder.load_file('main.kv')
class MainApp(App):
    cliente = None
    produto =None
    unidade = None

    def build(self):
        self.firebase = MyFireBase()
        return GUI
    

    def on_start(self):
        arquivos = os.listdir("icones/fotos_perfil")
        pagina_foto_perfil = self.root.ids['fotoperfilpage']
        lista_fotos = pagina_foto_perfil.ids['lista_fotos_perfil']
        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_perfil/{foto}", on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)

        self.carregar_infos_usuario()
    
        #carregar fotos clientes
        arquivos = os.listdir("icones/fotos_clientes")
        pagina_adicionar_vendas = self.root.ids['adicionarvendaspage']
        lista_clientes = pagina_adicionar_vendas.ids['lista_clientes']

        for foto_cliente in arquivos:
            imagem = ImageButton(source=f"icones/fotos_clientes/{foto_cliente}", 
                                 on_release=partial(self.selecionar_cliente, foto_cliente) )
            label = LabelButton(text=foto_cliente.replace('.png', '').capitalize(), 
                                on_release=partial(self.selecionar_cliente, foto_cliente) )

            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)

        #carregar fotos produtos
        arquivos = os.listdir("icones/fotos_produtos")
        lista_produtos = pagina_adicionar_vendas.ids['lista_produtos']

        for foto_produto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_produtos/{foto_produto}", on_release=partial(self.selecionar_produto, foto_produto))
            label = LabelButton(text=foto_produto.replace('.png', '').capitalize(), on_release=partial(self.selecionar_produto, foto_produto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)

        #carregar data
        pagina_adicionar_vendas.ids['label_data'].text = f"Data: {date.today().strftime('%d/%m/%Y')}"


    def carregar_infos_usuario(self):
        try:
            with open('refreshtoken.txt', 'r') as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token
        
            requisicao = requests.get(f"https://appvendaskivy-dfaa9-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}")
            requisicao_dic = requisicao.json()
            #foto perfil
            avatar = requisicao_dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids['foto_perfil']
            foto_perfil.source =  f"icones/fotos_perfil/{avatar}"

            #total vendas
            total_vendas = requisicao_dic['total_vendas']
            self.total_vendas = total_vendas
            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f"[b][color=#<000000>]Total de Vendas:  [/color]R$ {total_vendas}[/b]"

            #id vendedor
            id_vendedor = requisicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            paginas_ajustes = self.root.ids['ajustespage']
            paginas_ajustes.ids['id_vendedor'].text = f'Seu ID: {id_vendedor}'

            #preencher equipe
            self.equipe = requisicao_dic['equipe']

            try:
                vendas = requisicao_dic['vendas']
                pagina_homepage = self.root.ids['homepage']
                lista_vendas = pagina_homepage.ids['lista_vendas']
                self.vendas = vendas
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'], produto = venda['produto'],
                                        foto_produto = venda['foto_produto'], data=venda['data'], preco=venda['preco'],
                                        unidade=venda['unidade'], quantidade=venda['quantidade'])
                    lista_vendas.add_widget(banner)
            except:
                pass

            equipe = requisicao_dic['equipe']
            lista_equipe = equipe.split(",")
            pagina_lista_vendedores = self.root.ids['listarvendedorespage']
            lista_vendedores = pagina_lista_vendedores.ids['lista_vendedores']
            
            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor =  BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)
                    

            self.mudar_tela('homepage')
        except:
            pass


    def mudar_foto_perfil(self,foto, *args):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source =  f"icones/fotos_perfil/{foto}"
        info = f'{{"avatar": "{foto}"}}'
        requisicao = requests.patch(f"https://appvendaskivy-dfaa9-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                                    data=str(info))
        self.mudar_tela('ajustespage')
        

    def adicionar_vendedor(self, id_vendedor):
        pagina_add_vendedores = self.root.ids['adicionarvendedorespage']
        mensagem_vendedor = pagina_add_vendedores.ids['mensagem_vendedor']

        link = f'https://appvendaskivy-dfaa9-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor}"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        if not requisicao_dic:
            mensagem_vendedor.text = "Usuário não encontrado"
        else:
            equipe = self.equipe.split(',')
            if id_vendedor in equipe:
                mensagem_vendedor.text = "Vendedor já faz parte da equipe"
            else:
                self.equipe = self.equipe + f',{id_vendedor}'
                mensagem_vendedor.text = "Vendedor adicionado com sucesso!"
                info = f'{{"equipe": "{self.equipe}"}}'
                requisicao = requests.patch(f"https://appvendaskivy-dfaa9-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                                    data=str(info))
                #adicionar o banner do novo vendedor
                pagina_lista_vendedores = self.root.ids['listarvendedorespage']
                lista_vendedores = pagina_lista_vendedores.ids['lista_vendedores']
                banner_vendedor =  BannerVendedor(id_vendedor=id_vendedor)
                lista_vendedores.add_widget(banner_vendedor)
        

        
    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela

    
    def selecionar_cliente(self, foto, *args):
        pagina_adicionar_vendas = self.root.ids['adicionarvendaspage']
        lista_clientes = pagina_adicionar_vendas.ids['lista_clientes']
        self.cliente = foto.replace('.png', '')
        for item in list(lista_clientes.children):
            item.color = (1, 1, 1, 1)
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if texto == foto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_produto(self, foto, *args):
        pagina_adicionar_vendas = self.root.ids['adicionarvendaspage']
        lista_produtos = pagina_adicionar_vendas.ids['lista_produtos']
        self.produto = foto.replace('.png', '')
        for item in list(lista_produtos.children):
            item.color = (1, 1, 1, 1)
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if texto == foto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_unidade(self, id_label, *args):
        pagina_adicionar_vendas = self.root.ids['adicionarvendaspage']
        pagina_adicionar_vendas.ids['unidades_kg'].color = (1,1,1,1)
        pagina_adicionar_vendas.ids['unidades_unidades'].color = (1,1,1,1)
        pagina_adicionar_vendas.ids['unidades_litros'].color = (1,1,1,1)
        #marcar de azul o selecionado
        pagina_adicionar_vendas.ids[id_label].color = (0, 207/255, 219/255, 1)
        self.unidade = id_label.replace('unidades_', "")


    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto 
        unidade = self.unidade
        pagina_adicionar_venda = self.root.ids['adicionarvendaspage']
        data = pagina_adicionar_venda.ids['label_data'].text.replace('Data: ', "")
        preco= pagina_adicionar_venda.ids['preco_total'].text
        quantidade= pagina_adicionar_venda.ids['quantidade'].text

        if not cliente:
            pagina_adicionar_venda.ids['label_selecione_cliente'].color = (1,0,0,1)
        if not produto:
            pagina_adicionar_venda.ids['label_selecione_produto'].color = (1,0,0,1)
        if not unidade:
            pagina_adicionar_venda.ids['unidades_kg'].color = (1,0,0,1)
            pagina_adicionar_venda.ids['unidades_unidades'].color = (1,0,0,1)
            pagina_adicionar_venda.ids['unidades_litros'].color = (1,0,0,1)
        if not preco:
            pagina_adicionar_venda.ids['label_preco'].color = (1,0,0,1)
        else:
            try: 
                preco = float(preco)
            except:
                pagina_adicionar_venda.ids['label_preco'].color = (1,0,0,1)

        if not quantidade:
            pagina_adicionar_venda.ids['label_quantidade'].color = (1,0,0,1)
        else:
            try: 
                quantidade = float(quantidade)
            except:
                pagina_adicionar_venda.ids['label_quantidade'].color = (1,0,0,1)

        #Tudo preenchido
        if cliente and produto and unidade and preco and (type(preco)==float) and (type(quantidade)==float):
            foto_produto = produto + '.png'
            foto_cliente = cliente + '.png'

            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", "foto_produto": "{foto_produto}", "data": "{data}", "unidade": "{unidade}", "quantidade": "{quantidade}", "preco": "{preco}"}}'
            
            requests.post(f"https://appvendaskivy-dfaa9-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}", data=info)

            banner = BannerVenda(cliente=cliente, produto=produto, foto_cliente=foto_cliente,
                                foto_produto=foto_produto, preco=preco, quantidade=quantidade, unidade=unidade, data=data)
            
            pagina_homepage = self.root.ids['homepage']
            lista_vendas = pagina_homepage.ids['lista_vendas']
            lista_vendas.add_widget(banner)

            requisicao = requests.get(f"https://appvendaskivy-dfaa9-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}")
            total_vendas = float(requisicao.json())
            total_vendas += preco
            info = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f"https://appvendaskivy-dfaa9-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}", data=info)
            
            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f"[b][color=#<000000>]Total de Vendas:  [/color]R$ {total_vendas}[/b]"
            
            self.mudar_tela('homepage')


        self.cliente = None
        self.produto = None
        self.unidade = None

    
    def carregar_todas_vendas(self):
        todasvendaspage = self.root.ids['todasvendaspage']
        lista_todasvendas = todasvendaspage.ids['lista_vendas']

        for item in list(lista_todasvendas.children):
            lista_todasvendas.remove_widget(item)

        requisicao = requests.get(f'https://appvendaskivy-dfaa9-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requisicao_dic = requisicao.json()
        #foto perfil
        
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source =  f"icones/fotos_perfil/hash.png"


        total_vendas = 0
        for local_id_usuario in requisicao_dic:
            try:
                vendas = requisicao_dic[local_id_usuario]["vendas"]
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas += float(venda['preco'])
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'], produto = venda['produto'],
                                    foto_produto = venda['foto_produto'], data=venda['data'], preco=venda['preco'],
                                    unidade=venda['unidade'], quantidade=venda['quantidade'])
                    lista_todasvendas.add_widget(banner)

            except:
                pass

        #total vendas
        
        todasvendaspage.ids['label_total_vendas'].text = f"[b][color=#<000000>]Total de Vendas:  [/color]R$ {total_vendas}[/b]"
        self.mudar_tela('todasvendaspage')


    def sair_todas_vendas(self, id_tela):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f"icones/fotos_perfil/{self.avatar}"
        self.mudar_tela(id_tela)

    
    def carregar_vendas_vendedor(self, dic_vendedor, *args):
        vendasoutrovendedorpage = self.root.ids['vendasoutrovendedorpage']
        lista_outro_vendedor = vendasoutrovendedorpage.ids['lista_vendas']
        total_vendas = dic_vendedor['total_vendas']
        vendasoutrovendedorpage.ids['label_total_vendas'].text = f"[b][color=#<000000>]Total de Vendas:  [/color]R$ {total_vendas}[/b]"
        
        avatar = dic_vendedor['avatar']
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source =  f"icones/fotos_perfil/{avatar}"

        for item in list(lista_outro_vendedor.children):
            lista_outro_vendedor.remove_widget(item)

        try:
            vendas = dic_vendedor["vendas"]
            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'], produto = venda['produto'],
                                foto_produto = venda['foto_produto'], data=venda['data'], preco=venda['preco'],
                                unidade=venda['unidade'], quantidade=venda['quantidade'])
                lista_outro_vendedor.add_widget(banner)
        except:
            pass


        self.mudar_tela('vendasoutrovendedorpage')

        


MainApp().run()