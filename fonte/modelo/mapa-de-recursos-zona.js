  /* {{ZONA}} ==============================================================================
     MAPA DE RECURSOS — MODELO PARA A TUA ZONA (MGF no Plural, licença MIT)
     Este bloco é o único que precisas de mudar. O resto do ficheiro (categorias, filtros, pesquisa,
     lista para imprimir) fica igual em todas as zonas.

     1. Em ZONA, muda o nome da zona, o concelho, a descrição, o texto do botão «Vista …», o centro do
        mapa (latitude e longitude do centro de saúde; no Google Maps, botão direito no local e copiar
        as coordenadas), o zoom (14 é um bairro), as notas e as fontes.
     2. Em PAYLOAD.DATA, acrescenta um recurso por linha, separados por vírgulas, como no exemplo.
     3. Abre o ficheiro no browser para confirmar e envia-o para mgfplural@gmail.com, com o nome
        com que queres aparecer no site.

     Campos de cada recurso (só "id", "n", "c", "lat" e "lng" são obrigatórios):
       id  número único          n   nome                 c   categoria: saude, social, desporto, ensino, verde, cultura ou junta
       s   na saúde: SNS, Privados ou Convencionados       m   morada          t   telefone        e   email
       h   horário               o   observações          l   site (https://…)
       lat, lng  coordenadas      a   true se a localização for aproximada
       x   serviços (texto)      tg  lista de modalidades (desporto) ou especialidades (convencionados), ex.: ["Natação", "Judo"]
       sg  área do apoio social (ex.: "Idosos", "Infância")                   r   raio em metros (só espaços verdes)
     Exemplo:
       {"id": 1, "n": "Centro de Saúde de ...", "c": "saude", "s": "SNS", "m": "Rua ..., 0000-000 Localidade", "t": "210 000 000", "e": "", "h": "Dias úteis, 8h–20h", "o": "", "l": "", "lat": 38.7, "lng": -9.2, "a": false, "x": ""}
     ============================================================================================ */
  var ZONA = {
   "nome": "[Nome da zona]",
   "local": "[Concelho]",
   "descricao": "À volta do centro de saúde de <b>[Nome da zona]</b> — saúde, apoio social, desporto, ensino, cultura e espaços verdes. Pesquisa ou explora o mapa.",
   "vista": "Vista inicial",
   "centro": [
    39.6,
    -8.0
   ],
   "zoom": 7,
   "notas": [
    "<b>Fontes:</b> [onde foram recolhidos os recursos, por exemplo o guia de respostas sociais da câmara municipal]",
    "<b>Localizações:</b> [como foram obtidas as coordenadas; os pontos marcados como «localização aproximada» devem ser confirmados]. O botão <b>Direções</b> usa sempre a morada escrita.",
    "<b>Áreas verdes:</b> os círculos dos parques são esquemáticos e não correspondem aos limites reais.",
    "Informação sujeita a confirmação junto das instituições."
   ],
   "fontesImpressao": "[Fontes dos recursos.]",
   "vazio": "Ainda não há recursos neste mapa: é o modelo para a tua zona. Abre o ficheiro num editor de texto (ou pede à tua IA) e acrescenta os recursos no bloco «ZONA», como explicado no início desse bloco."
  };
  var PAYLOAD = {"DATA": [], "LINES": []};
  /* {{FIM-ZONA}} */
