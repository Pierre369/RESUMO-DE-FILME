"""
Serviço de Renderização de Vídeos Master de Alta Retenção (2 a 3 Minutos).
Integra:
1. Focal Tracking com Rede Neural OpenCV (YuNet ONNX) para enquadramento 1:1 e 9:16 impecável.
2. Legendas Dinâmicas Neon estilo TikTok (caixa alta, contorno vermelho vibrante, sincronia por frases).
3. Sincronização Milimétrica de Voz Dublada sem cortes de palavras e sem silêncios mortos.
4. Narração em 1ª Pessoa imersiva e cinematográfica com vozes neurais brasileiras calibradas.
"""

import os
import uuid
import json
import asyncio
import subprocess
from typing import Dict, Any, List, Optional
from core.focal_tracker import FocalTracker
from core.subtitle_service import SubtitleService
from app.services.media_service import MediaService
from app.services.voice_service import VoiceService
from app.services.project_service import ProjectService

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ==============================================================================
# DEFINIÇÃO DE TAKES MASTER (2 A 3 MINUTOS) — SINCRONIA MILIMÉTRICA REAL
# ==============================================================================

# 1. O MENU: O Golpe do X-Burguer (A Fuga Genial) — ~154s (2m34s)
MENU_CHEESEBURGER_BEATS = [
    {
        "id": "menu_cb_01",
        "type": "narration",
        "text": "Eu passei a noite inteira observando cada detalhe daquele restaurante bizarro. Todo mundo ali tava conformado em morrer, mas eu me recusei a ser cordeiro num matadouro gourmet.",
        "start": "01:27:10",
        "target_x": 960
    },
    {
        "id": "menu_cb_02",
        "type": "narration",
        "text": "Quando entrei na sala secreta do Chef, vi uma foto antiga dele jovem, sorrindo com orgulho virando hambúrguer numa lanchonete simples. Ali eu achei a única fraqueza do monstro.",
        "start": "01:27:45",
        "target_x": 960
    },
    {
        "id": "menu_cb_03",
        "type": "dialogue",
        "text": "Eu não gosto da sua comida. E eu gostaria de devolvê-la.",
        "start": "01:28:30.0",
        "duration": 7.5,
        "target_x": 1208
    },
    {
        "id": "menu_cb_04",
        "type": "narration",
        "text": "O salão inteiro parou em choque absoluto. Ninguém nunca tinha ousado reclamar da comida daquele cara na vida. O ego doentio dele estremeceu na hora.",
        "start": "01:28:42",
        "target_x": 960
    },
    {
        "id": "menu_cb_05",
        "type": "dialogue",
        "text": "Qual parte da minha comida não está do seu agrado? Para começar, você acabou com a alegria de comer.",
        "start": "01:28:56.5",
        "duration": 15.5,
        "target_x": 750
    },
    {
        "id": "menu_cb_06",
        "type": "narration",
        "text": "Eu olhei no fundo dos olhos dele e disse a verdade mais dolorosa: que a comida dele era fria, feita com obsessão doentia e que eu ainda tava morrendo de fome.",
        "start": "01:29:55",
        "target_x": 960
    },
    {
        "id": "menu_cb_07",
        "type": "dialogue",
        "text": "Com quanta fome? Eu estou faminta. Estar com vontade de quê? Um cheeseburger.",
        "start": "01:30:03.5",
        "duration": 14.5,
        "target_x": 1208
    },
    {
        "id": "menu_cb_08",
        "type": "dialogue",
        "text": "É, eu posso fazer um cheeseburger. Mas é um cheeseburger. Não é uma desconstrução chique sem sabor nenhum.",
        "start": "01:30:24.5",
        "duration": 11.5,
        "target_x": 728
    },
    {
        "id": "menu_cb_09",
        "type": "dialogue",
        "text": "Ao ponto. Com queijo americano. O queijo americano derrete sem despedaçar. Quanto vai custar? Dez dólares e noventa e cinco.",
        "start": "01:30:45.5",
        "duration": 11.5,
        "target_x": 1228
    },
    {
        "id": "menu_cb_10",
        "type": "dialogue",
        "text": "Ele vem com fritas? A fritadeira está ligada? Sim, chef!",
        "start": "01:30:57.5",
        "duration": 6.5,
        "target_x": 840
    },
    {
        "id": "menu_cb_11",
        "type": "narration",
        "text": "Pela primeira vez em décadas, os cozinheiros não tavam montando uma loucura artística sem sentido. Eles tavam fritando carne de verdade na chapa, sentindo o cheiro da comida que traz alegria de viver.",
        "start": "01:31:30",
        "target_x": 960
    },
    {
        "id": "menu_cb_12",
        "type": "dialogue",
        "text": "Isso é um cheeseburger. Infelizmente, acho que minha vontade foi maior que meu estômago.",
        "start": "01:33:08.5",
        "duration": 10.0,
        "target_x": 980
    },
    {
        "id": "menu_cb_13",
        "type": "dialogue",
        "text": "Eu posso levar para viagem? Um momento, por favor.",
        "start": "01:33:23.5",
        "duration": 13.0,
        "target_x": 1284
    },
    {
        "id": "menu_cb_14",
        "type": "dialogue",
        "text": "Obrigado por jantar no Hawthorn. Obrigada. Por tudo.",
        "start": "01:34:03.0",
        "duration": 16.0,
        "target_x": 750
    },
    {
        "id": "menu_cb_15",
        "type": "narration",
        "text": "Eu paguei os dez dólares, peguei a sacola e saí andando pela porta da frente. Enquanto a ilha inteira ardia em chamas com todos lá dentro, eu comi o melhor cheeseburger da minha vida sã e salva no barco.",
        "start": "01:39:40",
        "target_x": 960
    }
]

# 2. O MENU: A Revelação da Morte (As Palmas Mortais) — ~135s (2m15s)
MENU_DEATH_BEATS = [
    {
        "id": "menu_death_01",
        "type": "narration",
        "text": "A balsa chegou na ilha isolada e tudo parecia um evento exclusivo pra ricaços esnobes pagarem fortunas por comida conceitual.",
        "start": "00:06:20",
        "target_x": 960
    },
    {
        "id": "menu_death_02",
        "type": "narration",
        "text": "A recepção foi estranha, parecendo uma seita militar. Mas o verdadeiro pesadelo começou quando o Chef Slowik bateu a primeira palma no meio do salão.",
        "start": "00:23:40",
        "target_x": 960
    },
    {
        "id": "menu_death_03",
        "type": "dialogue",
        "text": "Chef bate a palma e o salão silencia imediatamente com tensão",
        "start": "00:23:48",
        "duration": 8.0,
        "target_x": 960
    },
    {
        "id": "menu_death_04",
        "type": "narration",
        "text": "Ele começou a apresentar pratos bizarros, como um prato de pão sem nenhum pão, apenas molhos. Os convidados achavam genial, mas eu sabia que tinha veneno no ar.",
        "start": "00:27:15",
        "target_x": 960
    },
    {
        "id": "menu_death_05",
        "type": "dialogue",
        "text": "Chef apresenta a filosofia implacável do menu aos convidados",
        "start": "00:33:10",
        "duration": 8.5,
        "target_x": 960
    },
    {
        "id": "menu_death_06",
        "type": "narration",
        "text": "De repente, no meio da apresentação, um dos cozinheiros sacou uma arma e tirou a própria vida na frente de todos. Foi quando o pânico engoliu o restaurante.",
        "start": "00:46:15",
        "target_x": 960
    },
    {
        "id": "menu_death_07",
        "type": "dialogue",
        "text": "Até o final da noite, todos nós teremos morrido juntos.",
        "start": "00:46:52",
        "duration": 11.5,
        "target_x": 960
    },
    {
        "id": "menu_death_08",
        "type": "narration",
        "text": "Eles tentaram correr pras portas, mas os seguranças bloquearam tudo. O restaurante era uma câmara de execução planejada nos mínimos segundos.",
        "start": "00:48:20",
        "target_x": 960
    },
    {
        "id": "menu_death_09",
        "type": "dialogue",
        "text": "Chef confronta os convidados sobre suas mentiras e hipocrisias",
        "start": "00:58:33",
        "duration": 7.5,
        "target_x": 960
    },
    {
        "id": "menu_death_10",
        "type": "narration",
        "text": "O Chef me chamou no canto e confessou que eu não deveria estar ali. Eu era uma acompanhante contratada na última hora, fora do plano dele.",
        "start": "01:03:15",
        "target_x": 960
    },
    {
        "id": "menu_death_11",
        "type": "dialogue",
        "text": "Você quer morrer com quem serve ou com quem consome?",
        "start": "01:07:17",
        "duration": 9.0,
        "target_x": 960
    },
    {
        "id": "menu_death_12",
        "type": "narration",
        "text": "Ali eu percebi a verdade: implorar não ia adiantar nada com um psicopata perfeccionista. Se eu quisesse ver o sol nascer de novo, eu ia ter que virar o jogo na própria mente dele.",
        "start": "01:13:00",
        "target_x": 960
    },
    {
        "id": "menu_death_13",
        "type": "dialogue",
        "text": "Chef prepara a sobremesa final enquanto o salão queima",
        "start": "01:37:15",
        "duration": 10.0,
        "target_x": 960
    },
    {
        "id": "menu_death_14",
        "type": "narration",
        "text": "Aquele jantar não era sobre comida, era sobre julgamento. E quem não sabe jogar com as regras do monstro se torna o próximo prato servido.",
        "start": "01:39:10",
        "target_x": 960
    }
]

# 3. O MENU: A Humilhação de Tyler na Cozinha — ~130s (2m10s)
MENU_TYLER_BEATS = [
    {
        "id": "menu_tyler_01",
        "type": "narration",
        "text": "O Tyler passou a noite inteira tirando fotos de cada prato, se achando um crítico culinário genial e bajulando o Chef a cada segundo.",
        "start": "00:14:40",
        "target_x": 960
    },
    {
        "id": "menu_tyler_02",
        "type": "dialogue",
        "text": "Tyler exalta a culinária do Chef com afetação exagerada",
        "start": "00:18:45",
        "duration": 6.5,
        "target_x": 960
    },
    {
        "id": "menu_tyler_03",
        "type": "narration",
        "text": "Ele sabia desde o início que todo mundo no restaurante ia morrer, e mesmo assim me contratou pra vir junto só pra não perder a reserva dele.",
        "start": "01:06:50",
        "target_x": 960
    },
    {
        "id": "menu_tyler_04",
        "type": "dialogue",
        "text": "Chef expõe a covardia de Tyler na frente de todo o salão",
        "start": "01:07:42",
        "duration": 8.0,
        "target_x": 960
    },
    {
        "id": "menu_tyler_05",
        "type": "dialogue",
        "text": "Cozinhe para nós, Tyler. Mostre seu talento culinário.",
        "start": "01:09:09",
        "duration": 7.0,
        "target_x": 960
    },
    {
        "id": "menu_tyler_06",
        "type": "narration",
        "text": "O sangue dele sumiu do rosto. O cara que se dizia entendedor de gastronomia foi obrigado a vestir a dólmã e encarar as panelas sob os olhares de todos.",
        "start": "01:09:25",
        "target_x": 960
    },
    {
        "id": "menu_tyler_07",
        "type": "dialogue",
        "text": "Chef humilha as tentativas desastradas e o desespero de Tyler",
        "start": "01:09:58",
        "duration": 8.5,
        "target_x": 960
    },
    {
        "id": "menu_tyler_08",
        "type": "narration",
        "text": "Ele tremia tanto que mal conseguia segurar a faca. Cortou uma carne crua, jogou alho-poró de qualquer jeito e fez uma gosma intragável.",
        "start": "01:10:40",
        "target_x": 960
    },
    {
        "id": "menu_tyler_09",
        "type": "dialogue",
        "text": "Chef batiza o prato medíocre de Papo Furado do Tyler",
        "start": "01:11:18",
        "duration": 7.0,
        "target_x": 960
    },
    {
        "id": "menu_tyler_10",
        "type": "narration",
        "text": "O Chef deu uma garfada na gororoba, cuspiu no chão e destruiu o que restava do ego do moleque na frente da mulher que ele queria impressionar.",
        "start": "01:11:45",
        "target_x": 960
    },
    {
        "id": "menu_tyler_11",
        "type": "dialogue",
        "text": "Chef sussurra algo sombrio e devastador no ouvido de Tyler",
        "start": "01:12:15",
        "duration": 6.5,
        "target_x": 960
    },
    {
        "id": "menu_tyler_12",
        "type": "narration",
        "text": "Tyler tirou a dólmã em choque, entrou na despensa e tirou a própria vida. Foi o aviso final do Chef: naquele jantar, a vaidade cobra o preço mais alto.",
        "start": "01:15:55",
        "target_x": 960
    },
    {
        "id": "menu_tyler_13",
        "type": "narration",
        "text": "Ali eu soube que não tinha mais espaço pra erros. Cada segundo contava pra encontrar uma saída antes da sobremesa final.",
        "start": "01:16:30",
        "target_x": 960
    }
]

# 4. PALMER: O Acerto de Contas no Bar — ~141s (2m21s)
PALMER_BAR_BEATS = [
    {
        "id": "palmer_bar_01",
        "type": "narration",
        "text": "Eu passei doze anos na cadeia e tudo o que eu queria quando saí era viver em paz, trabalhar de zelador e não arrumar confusão com ninguém.",
        "start": "00:08:15",
        "target_x": 756
    },
    {
        "id": "palmer_bar_02",
        "type": "narration",
        "text": "Mas a vida colocou o pequeno Sam no meu caminho. Um garoto puro, abandonado pela mãe e que só queria alguém que o protegesse desse mundo cruel.",
        "start": "00:30:10",
        "target_x": 756
    },
    {
        "id": "palmer_bar_03",
        "type": "dialogue",
        "text": "Escuta, garoto. Às vezes tem que revidar. Se não se defender agora, eles nunca vão te deixar em paz.",
        "start": "01:13:30.0",
        "duration": 15.0,
        "target_x": 680
    },
    {
        "id": "palmer_bar_04",
        "type": "dialogue",
        "text": "Eddie, não eram garotos. Como assim? Quem fez isso com você, Sam? O pai do Toby. E um amigo dele, Daryl. Foi ele.",
        "start": "01:13:45.0",
        "duration": 24.5,
        "target_x": 680
    },
    {
        "id": "palmer_bar_05",
        "type": "narration",
        "text": "Quando eu vi as lágrimas no rosto daquela criança indefesa e soube que dois marmanjos tinham batido nele, toda a minha promessa de nunca mais voltar pra cadeia evaporou na mesma hora.",
        "start": "01:14:10",
        "target_x": 756
    },
    {
        "id": "palmer_bar_06",
        "type": "dialogue",
        "text": "Eddie. Eddie! Pra onde tá indo? Eddie, não faz isso!",
        "start": "01:14:15.5",
        "duration": 7.0,
        "target_x": 756
    },
    {
        "id": "palmer_bar_07",
        "type": "narration",
        "text": "Eu entrei na caminhonete cego de ódio. Fui direto pro bar da cidade onde aqueles covardes costumavam beber e rir das próprias covardias.",
        "start": "01:14:35",
        "target_x": 756
    },
    {
        "id": "palmer_bar_08",
        "type": "dialogue",
        "text": "Achou engraçado, Daryl? Ver um adulto segurar um garotinho e fazer ele chorar passando maquiagem na cara?",
        "start": "01:14:56.5",
        "duration": 9.0,
        "target_x": 840
    },
    {
        "id": "palmer_bar_09",
        "type": "dialogue",
        "text": "Eu vou deixar uma coisa bem clara. Fica longe do Sam. Se você encostar um dedo nele de novo, você não vai fugir dessa vez. Pode acreditar!",
        "start": "01:15:08.5",
        "duration": 11.0,
        "target_x": 840
    },
    {
        "id": "palmer_bar_10",
        "type": "narration",
        "text": "Eu atravessei o salão e quebrei a cara daquele desgraçado no balcão. Ninguém no bar teve coragem de se meter entre mim e ele.",
        "start": "01:15:25",
        "target_x": 756
    },
    {
        "id": "palmer_bar_11",
        "type": "dialogue",
        "text": "Vai fazer o quê? Bater em todo mundo que mexer com ele? Não, só em quem tem mais de trinta.",
        "start": "01:15:52.5",
        "duration": 8.5,
        "target_x": 756
    },
    {
        "id": "palmer_bar_12",
        "type": "dialogue",
        "text": "Tem outras formas de resolver as coisas. Vai arranjar problema.",
        "start": "01:16:00.5",
        "duration": 9.5,
        "target_x": 756
    },
    {
        "id": "palmer_bar_13",
        "type": "narration",
        "text": "Eu posso voltar pra cadeia pelo resto da vida se for preciso, mas por aquele menino que me ensinou a amar de novo, eu enfrentaria o mundo inteiro sem hesitar um segundo.",
        "start": "01:16:25",
        "target_x": 756
    }
]

# 5. JOHN WICK: A Invasão da Casa e o Despertar do Baba Yaga — ~145s (2m25s)
JW_INVASION_BEATS = [
    {
        "id": "jw_inv_01",
        "type": "narration",
        "text": "Eu enterrei minha esposa Helen e tudo o que me restou no mundo foi uma cachorrinha filhote que ela me enviou antes de partir, pra me lembrar que eu ainda podia amar.",
        "start": "00:07:08",
        "target_x": 960
    },
    {
        "id": "jw_inv_02",
        "type": "dialogue",
        "text": "Belo carro. Mustang 69. Quanto quer por ele? Não está à venda.",
        "start": "00:11:46",
        "duration": 6.5,
        "target_x": 1200
    },
    {
        "id": "jw_inv_03",
        "type": "narration",
        "text": "Aquele moleque mimado da máfia russa não aceitou ouvir um não. Ele anotou a placa do meu Mustang e seguiu o rastro até a minha casa.",
        "start": "00:12:10",
        "target_x": 960
    },
    {
        "id": "jw_inv_04",
        "type": "narration",
        "text": "No meio da madrugada, enquanto eu dormia, sombras armadas invadiram a casa no escuro.",
        "start": "00:13:50",
        "target_x": 960
    },
    {
        "id": "jw_inv_05",
        "type": "dialogue",
        "text": "Invasão violenta: Iosef espanca John no escuro e rouba o carro",
        "start": "00:14:20",
        "duration": 8.5,
        "target_x": 960
    },
    {
        "id": "jw_inv_06",
        "type": "narration",
        "text": "Eles me espancaram com barras de ferro, roubaram o Mustang e mataram o cachorrinho indefeso na minha frente. Eles tiraram a única ponta de paz que me prendia à humanidade.",
        "start": "00:14:55",
        "target_x": 500
    },
    {
        "id": "jw_inv_07",
        "type": "dialogue",
        "text": "Aurelio revela para Viggo que o dono do carro é John Wick",
        "start": "00:20:18",
        "duration": 6.0,
        "target_x": 960
    },
    {
        "id": "jw_inv_08",
        "type": "narration",
        "text": "Quando a notícia chegou no chefe da máfia Viggo Tarasov, o sangue dele congelou. Ele sabia exatamente o monstro adormecido que o próprio filho tinha acordado.",
        "start": "00:22:45",
        "target_x": 960
    },
    {
        "id": "jw_inv_09",
        "type": "dialogue",
        "text": "Ele não era exatamente o Bicho-Papão. Ele era quem você mandava pra matar a porra do Bicho-Papão!",
        "start": "00:24:00",
        "duration": 13.5,
        "target_x": 600
    },
    {
        "id": "jw_inv_10",
        "type": "narration",
        "text": "Eu desci até o porão da minha casa. Peguei a marreta de demolição mais pesada que tinha e comecei a bater no chão de concreto.",
        "start": "00:24:45",
        "target_x": 960
    },
    {
        "id": "jw_inv_11",
        "type": "dialogue",
        "text": "John marreta o piso e desenterra o arsenal escondido",
        "start": "00:25:35",
        "duration": 8.0,
        "target_x": 1550
    },
    {
        "id": "jw_inv_12",
        "type": "narration",
        "text": "Sob o concreto quebrado tava o baú de armas, munições perfurantes e as moedas de ouro do Continental. O homem de família tinha morrido naquela noite.",
        "start": "00:26:10",
        "target_x": 960
    },
    {
        "id": "jw_inv_13",
        "type": "dialogue",
        "text": "Viggo tenta negociar pelo telefone e John desliga em silêncio absoluto",
        "start": "00:31:30",
        "duration": 8.0,
        "target_x": 960
    },
    {
        "id": "jw_inv_14",
        "type": "narration",
        "text": "Eles acharam que eu tava aposentado. Mas depois daquela noite, o submundo inteiro de Nova York ia lembrar por que ninguém vivo mexe com John Wick.",
        "start": "00:34:20",
        "target_x": 960
    }
]


class RenderService:
    def __init__(self):
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        self.project_service = ProjectService()
        self.voice_service = VoiceService()

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        return self.active_jobs.get(job_id, {"status": "not_found", "progress": 0})

    def select_beats_for_scene(
        self,
        movie_path: str,
        scene_id: Optional[str] = None,
        scene_name: Optional[str] = None,
        narrator_voice: str = "Protagonista",
        orig_w: int = 1920,
        orig_h: int = 1080,
        dur_total: float = 5400.0
    ) -> List[Dict[str, Any]]:
        """
        Seleciona a lista completa de takes de 2 a 3 minutos baseada no filme e na cena escolhida.
        Se for um filme genérico, monta um arco dramático de 13 takes de alta intensidade.
        """
        movie_lower = movie_path.lower()
        s_id = (scene_id or "").lower()
        s_name = (scene_name or "").lower()

        # O MENU
        if "menu" in movie_lower:
            if "palmas" in s_name or "morte" in s_name or "death" in s_id:
                return MENU_DEATH_BEATS
            elif "tyler" in s_name or "cozinha" in s_name or "tyler" in s_id:
                return MENU_TYLER_BEATS
            else:
                return MENU_CHEESEBURGER_BEATS

        # JOHN WICK
        elif "wick" in movie_lower or "john" in movie_lower:
            return JW_INVASION_BEATS

        # PALMER
        elif "palmer" in movie_lower:
            return PALMER_BAR_BEATS

        # FILME GENÉRICO OU NOVO UPLOAD (Gera arco narrativo completo de 2 a 3 minutos)
        else:
            mid = dur_total * 0.35
            generic_narration_texts = [
                "Eu nunca imaginei que aquele dia comum ia se transformar no maior pesadelo da minha vida.",
                "Quando eu olhei ao redor, percebi que ninguém ali tava jogando limpo. A armadilha já tava montada.",
                "Ele achou que podia me intimidar e passar por cima de tudo sem pagar o preço.",
                "Naquele segundo, toda a paciência que eu guardei por anos simplesmente desapareceu.",
                "Eu encarei a ameaça de frente e deixei bem claro que quem cruza meu caminho não tem segunda chance.",
                "Eles tentaram virar o jogo contra mim, mas já era tarde demais pra recuar.",
                "No final das contas, o recado ficou gravado na memória de todos: nunca subestime quem não tem mais nada a perder."
            ]
            generic_beats = []
            for i in range(13):
                sec = mid + (i * 22)
                ts = f"{int(sec // 3600):02d}:{int((sec % 3600) // 60):02d}:{sec % 60:05.2f}"
                if i % 2 == 0:
                    text_idx = min(i // 2, len(generic_narration_texts) - 1)
                    generic_beats.append({
                        "id": f"gen_nar_{i+1:02d}",
                        "type": "narration",
                        "text": generic_narration_texts[text_idx],
                        "start": ts,
                        "target_x": orig_w // 2
                    })
                else:
                    generic_beats.append({
                        "id": f"gen_dial_{i+1:02d}",
                        "type": "dialogue",
                        "text": "Confronto e revelação intensa",
                        "start": ts,
                        "duration": 8.0,
                        "target_x": orig_w // 2
                    })
            return generic_beats

    async def _render_beats_pipeline(
        self,
        beats: List[Dict[str, Any]],
        movie_path: str,
        orig_w: int,
        orig_h: int,
        aspect_ratio: str,
        work_dir: str,
        output_path: str,
        narrator_voice: str,
        job_id: str,
        audio_stream_map: str = "0:a:0"
    ):
        """Pipeline mestre com corte milimétrico, focal tracking por OpenCV YuNet e legendas dinâmicas estilo TikTok."""
        rendered_segments = []
        total_beats = len(beats)

        for idx, b in enumerate(beats):
            bid = b["id"]
            seg_video = os.path.join(work_dir, f"{bid}.mp4")
            sub_ass = os.path.join(work_dir, f"{bid}.ass")

            # 1. Visão Computacional Neural YuNet para detecção facial e enquadramento ótimo
            optimal_x = FocalTracker.detect_optimal_target_x(
                movie_path=movie_path,
                start_ts=str(b["start"]),
                orig_w=orig_w,
                orig_h=orig_h,
                fallback_x=b.get("target_x", orig_w // 2)
            )
            vf_crop = FocalTracker.get_ffmpeg_crop_filter(orig_w, orig_h, optimal_x, aspect_ratio)

            # 2. Atualiza status de progresso no monitor
            pct = 10 + int((idx / total_beats) * 85)
            b_desc = "diálogo original dublado" if b["type"] == "dialogue" else "narração em 1ª pessoa"
            self.active_jobs[job_id].update({
                "progress": pct,
                "step": f"Renderizando take {idx+1}/{total_beats} ({b_desc}) com foco facial YuNet & legendas TikTok..."
            })

            if b["type"] == "dialogue":
                # Diálogo dublado com normalização de áudio e legendas embutidas
                SubtitleService.generate_ass_file(
                    text=b["text"],
                    duration=float(b["duration"]),
                    output_ass_path=sub_ass,
                    aspect_ratio=aspect_ratio
                )
                norm_sub = sub_ass.replace("\\", "/").replace(":", "\\:")
                full_vf = f"{vf_crop},subtitles='{norm_sub}'"

                cmd = [
                    "ffmpeg", "-y", "-ss", str(b["start"]), "-t", str(b["duration"]),
                    "-i", movie_path,
                    "-map", "0:v:0", "-map", audio_stream_map,
                    "-vf", full_vf,
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aformat=channel_layouts=stereo",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    seg_video
                ]
                await asyncio.to_thread(subprocess.run, cmd, check=True, capture_output=True)

            else:
                # Síntese de voz com Edge-TTS Neural PT-BR calibrado (ou Fish Audio)
                tts_mp3 = os.path.join(work_dir, f"{bid}_tts.mp3")
                await self.voice_service.generate_speech(
                    text=b["text"],
                    character_name=narrator_voice,
                    movie_path=movie_path,
                    output_audio_path=tts_mp3,
                    speed_rate="+12%"
                )

                # Mede a duração exata do áudio da fala gerada
                probe = subprocess.run([
                    "ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "csv=p=0", tts_mp3
                ], capture_output=True, text=True, check=True)
                dur = float(probe.stdout.strip())
                video_dur = dur + 0.10  # transição milimétrica contínua (sem pausas mortas)

                # Gera arquivo de legendas .ass sincronizado com a narração
                SubtitleService.generate_ass_file(
                    text=b["text"],
                    duration=dur,
                    output_ass_path=sub_ass,
                    aspect_ratio=aspect_ratio
                )
                norm_sub = sub_ass.replace("\\", "/").replace(":", "\\:")
                full_vf = f"{vf_crop},subtitles='{norm_sub}'"

                raw_clip = os.path.join(work_dir, f"{bid}_raw.mp4")
                cmd_raw = [
                    "ffmpeg", "-y", "-ss", str(b["start"]), "-t", f"{video_dur:.2f}",
                    "-i", movie_path,
                    "-map", "0:v:0", "-map", audio_stream_map,
                    "-vf", full_vf,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    raw_clip
                ]
                await asyncio.to_thread(subprocess.run, cmd_raw, check=True, capture_output=True)

                # Mixagem de alta qualidade: ambiência do filme abaixada (-22dB) + voz narrativa cristalina
                cmd_mix = [
                    "ffmpeg", "-y",
                    "-i", raw_clip,
                    "-i", tts_mp3,
                    "-filter_complex",
                    "[0:a]aformat=channel_layouts=stereo,volume=0.08[bg];[1:a]aformat=channel_layouts=stereo,volume=1.0[vox];[bg][vox]amix=inputs=2:duration=first:dropout_transition=1[aout]",
                    "-map", "0:v", "-map", "[aout]",
                    "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    seg_video
                ]
                await asyncio.to_thread(subprocess.run, cmd_mix, check=True, capture_output=True)

            rendered_segments.append(seg_video)

        # Concatenação final com compatibilidade absoluta
        self.active_jobs[job_id].update({
            "progress": 96,
            "step": f"Concatenando {total_beats} takes master e finalizando vídeo de alta retenção (2-3 min)..."
        })

        concat_txt = os.path.join(work_dir, "concat_list.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for s in rendered_segments:
                norm = s.replace("\\", "/")
                f.write(f"file '{norm}'\n")

        cmd_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_txt,
            "-c", "copy", "-movflags", "+faststart",
            output_path
        ]
        await asyncio.to_thread(subprocess.run, cmd_concat, check=True, capture_output=True)

    async def render_scene_async(
        self,
        job_id: str,
        movie_path: str,
        aspect_ratio: str,
        narrator_voice: str,
        scene_id: Optional[str] = None,
        scene_name: Optional[str] = None,
        screenplay_text: Optional[str] = None,
        output_filename: str = "video_app_render.mp4",
        project_id: Optional[str] = None
    ):
        """Executa a renderização completa atualizando o progresso em tempo real."""
        self.active_jobs[job_id] = {
            "status": "processing",
            "progress": 5,
            "step": "Analisando dimensões do vídeo e trilha de dublagem PT-BR...",
            "output_url": None,
            "project_id": project_id
        }

        output_path = os.path.join(BASE_DIR, "output", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        work_dir = os.path.join(BASE_DIR, "app", "temp_render", job_id)
        os.makedirs(work_dir, exist_ok=True)

        try:
            await asyncio.sleep(0.3)
            # 1. Proba o arquivo para pegar largura, altura, duração e canal de áudio
            info = MediaService.probe_file(movie_path)
            orig_w = info.get("width", 1920)
            orig_h = info.get("height", 1080)
            dur_total = info.get("duration", 5400.0)
            audio_stream_map = MediaService.get_best_audio_stream_map(movie_path)

            voice_status = self.voice_service.get_key_status()
            engine_name = voice_status["provider"]

            self.active_jobs[job_id].update({
                "progress": 10,
                "step": f"Inicializando motor de voz ({engine_name}), enquadramento YuNet {aspect_ratio} ({orig_w}x{orig_h}) e legendas TikTok..."
            })

            # 2. Seleciona os takes específicos para a cena e filme escolhidos
            beats = self.select_beats_for_scene(
                movie_path=movie_path,
                scene_id=scene_id,
                scene_name=scene_name,
                narrator_voice=narrator_voice,
                orig_w=orig_w,
                orig_h=orig_h,
                dur_total=dur_total
            )

            # 3. Executa a decupagem e renderização completa
            await self._render_beats_pipeline(
                beats=beats,
                movie_path=movie_path,
                orig_w=orig_w,
                orig_h=orig_h,
                aspect_ratio=aspect_ratio,
                work_dir=work_dir,
                output_path=output_path,
                narrator_voice=narrator_voice,
                job_id=job_id,
                audio_stream_map=audio_stream_map
            )

            # 4. Conclusão com sucesso
            output_url = f"/output/{output_filename}"
            self.active_jobs[job_id] = {
                "status": "completed",
                "progress": 100,
                "step": f"Vídeo master TikTok de alta retenção (2-3 min) finalizado com sucesso! ({engine_name})",
                "output_url": output_url,
                "project_id": project_id
            }

            # Atualiza projeto no banco local
            if project_id:
                self.project_service.update_project(
                    project_id=project_id,
                    status="completed",
                    progress=100,
                    output_url=output_url,
                    cuts_count=len(beats)
                )

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.active_jobs[job_id] = {
                "status": "error",
                "progress": 0,
                "step": f"Falha na renderização: {str(e)}",
                "output_url": None,
                "project_id": project_id
            }
            if project_id:
                self.project_service.update_project(
                    project_id=project_id,
                    status="error",
                    progress=0
                )
