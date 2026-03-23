import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Asegura que el paquete `src/` esté en el path cuando se ejecuta desde la raíz
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from DI.continer import SearchContainer
from DataAcquisitionModule.Scraper.scrapedDocument import ScrapedDocument

container = SearchContainer()
container.wire(modules=[__name__])

async def main():
    index_service = container.index_service()
    
    # Tus documentos scraped
    scraped_docs = [
    ScrapedDocument(
        source="bbc",
        url="https://example.com/noticia-1",
        url_normalized="https://example.com/noticia-1",
        title="La economía global muestra signos de recuperación",
        content="La economía mundial está mostrando señales de recuperación tras la crisis reciente. Expertos destacan el crecimiento en varios sectores clave.",
        authors=["Juan Pérez"],
        date=datetime(2024, 3, 10),
        indexed=False,
        embeddings_generated=False
    ),
    # Economía
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/economia/2024/01", 
        url_normalized="https://cubadebate.cu/economia/2024/01",
        title="La economía cubana muestra signos de recuperación",
        content="La economía cubana está mostrando signos de recuperación tras un período difícil. Los sectores turístico y agrícola han liderado el crecimiento. El gobierno ha implementado nuevas políticas para estimular la inversión extranjera.",
        authors=["María García"], date=datetime(2024, 1, 15), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/economia/2024/02",
        url_normalized="https://cubadebate.cu/economia/2024/02",
        title="Sector turístico cubano supera expectativas",
        content="El sector turístico de Cuba ha superado las expectativas de crecimiento este año. Los hoteles报告显示 una ocupación promedio del 85%. Los expertos prevén que el turismo seguirá siendo el motor de la economía nacional.",
        authors=["Carlos López"], date=datetime(2024, 1, 20), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/economia/2024/03",
        url_normalized="https://cubadebate.cu/economia/2024/03",
        title="Inversiones extranjeras en Cuba aumentan",
        content="Las inversiones extranjeras en Cuba han aumentado significativamente en los últimos meses. Empresas de España, México y Canadá han mostrado interés en el mercado cubano. Los sectores más atractivos son el turismo y la energía renovable.",
        authors=["Ana Martínez"], date=datetime(2024, 2, 5), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/economia/2024/04",
        url_normalized="https://cubadebate.cu/economia/2024/04",
        title="Producción agrícola supera metas establecidas",
        content="La producción agrícola en Cuba ha superado las metas establecidas para este año. Los cultivos de arroz y frijoles han tenido un buen rendimiento. El gobierno ha invertido en tecnología agrícola para mejorar la eficiencia.",
        authors=["Pedro Sánchez"], date=datetime(2024, 2, 10), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/economia/2024/05",
        url_normalized="https://cubadebate.cu/economia/2024/05",
        title="Crisis económica mundial afecta mercados",
        content="La crisis económica mundial está afectando los mercados internacionales. Los precios del petróleo han bajado y las monedas latinoamericanas se han depreciado. Los analistas warn about la situación económica global.",
        authors=["Laura Rodríguez"], date=datetime(2024, 2, 15), indexed=False, embeddings_generated=False
    ),
    
    # Política
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/politica/2024/01",
        url_normalized="https://cubadebate.cu/politica/2024/01",
        title="Gobierno anuncia nuevas políticas públicas",
        content="El gobierno ha anunciado nuevas políticas públicas para mejorar la educación y la salud. Se invertirá en escuelas y hospitales en todo el país. Las autoridades aseguran que estas medidas beneficiarán a la población.",
        authors=["Juan Pérez"], date=datetime(2024, 1, 18), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/politica/2024/02",
        url_normalized="https://cubadebate.cu/politica/2024/02",
        title="Elecciones municipales serán en 2024",
        content="Las elecciones municipales se celebrarán en el mes de octubre de 2024. Los ciudadanos podrán elegir a sus representantes locales. El proceso electoral será supervisado por organismos internacionales.",
        authors=["Carmen Torres"], date=datetime(2024, 2, 1), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/politica/2024/03",
        url_normalized="https://cubadebate.cu/politica/2024/03",
        title="Relaciones diplomáticas con países vecinos",
        content="Cuba fortalece sus relaciones diplomáticas con países vecinos del Caribe. Se han firmado acuerdos de cooperación en áreas como comercio, cultura y educación. Los embajadores han destacado la importancia del diálogo.",
        authors=["Roberto Díaz"], date=datetime(2024, 2, 8), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/politica/2024/04",
        url_normalized="https://cubadebate.cu/politica/2024/04",
        title="Reforma del sistema judicial avanza",
        content="La reforma del sistema judicial continúa avanzando en el país. Se han implementado nuevos mecanismos para garantizar la transparencia y el acceso a la justicia. Los abogados han participado en la elaboración de las nuevas leyes.",
        authors=["Sofia Hernández"], date=datetime(2024, 2, 20), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/politica/2024/05",
        url_normalized="https://cubadebate.cu/politica/2024/05",
        title="Partido político celebra congreso nacional",
        content="El partido político ha celebrado su congreso nacional con la participación de delegados de todo el país. Se han definido las líneas estratégicas para los próximos años. Los líderes han destacado la unidad del pueblo.",
        authors=["Miguel Fernández"], date=datetime(2024, 3, 1), indexed=False, embeddings_generated=False
    ),
    
    # Salud
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/salud/2024/01",
        url_normalized="https://cubadebate.cu/salud/2024/01",
        title="Nuevo hospital inaugurated en La Habana",
        content="Un nuevo hospital ha sido inaugurado en La Habana con modernas instalaciones. El centro médico cuenta con tecnología de punta y personal especializado. Los pacientes podrán acceder a servicios de alta calidad.",
        authors=["Elena Vargas"], date=datetime(2024, 1, 22), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/salud/2024/02",
        url_normalized="https://cubadebate.cu/salud/2024/02",
        title="Programa de vacunación cubre a toda la población",
        content="El programa de vacunación ha cubierto a toda la población del país. Las autoridades sanitarias reportan altas tasas de inmunización. Las enfermedades prevenibles han disminuido significativamente.",
        authors=["Jorge Morales"], date=datetime(2024, 2, 3), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/salud/2024/03",
        url_normalized="https://cubadebate.cu/salud/2024/03",
        title="Médicos cubanos colaboran en el exterior",
        content="Médicos cubanos continúan colaborando en programas de salud en el exterior. Brigadas médicas han sido enviadas a países de África y América Latina. Los profesionales de la salud han recibido reconocimientos internacionales.",
        authors=["Patricia Reyes"], date=datetime(2024, 2, 12), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/salud/2024/04",
        url_normalized="https://cubadebate.cu/salud/2024/04",
        title="Investigación sobre nuevas medicinas avanza",
        content="Investigadores cubanos avanzan en el desarrollo de nuevas medicinas. Los laboratorios han desarrollado tratamientos innovadores para diversas enfermedades. Los resultados de los estudios clínicos son prometedores.",
        authors=["Andrés Castro"], date=datetime(2024, 2, 18), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/salud/2024/05",
        url_normalized="https://cubadebate.cu/salud/2024/05",
        title="Sistema de salud fortalece atención primaria",
        content="El sistema de salud fortalece la atención primaria en todo el territorio nacional. Se han construido nuevos consultorios del médico de la familia. Los servicios de emergencia han mejorado significativamente.",
        authors=["Lucía Méndez"], date=datetime(2024, 2, 25), indexed=False, embeddings_generated=False
    ),
    
    # Deportes
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/deportes/2024/06",
        url_normalized="https://cubadebate.cu/deportes/2024/06",
        title="El deporte en cuba crece",
        content="El equipo nacional de baseball ha clasificado para el campeonato mundial. Los jugadores han demostrado un excelente desempeño en las clasificatorias. Los herramientfanáticos esperan con ansias la competencia internacional.",
        authors=["Raúl Ortega"], date=datetime(2024, 1, 25), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/deportes/2024/01",
        url_normalized="https://cubadebate.cu/deportes/2024/01",
        title="Equipo de baseball clasifica para el mundial",
        content="El equipo nacional de baseball ha clasificado para el campeonato mundial. Los jugadores han demostrado un excelente desempeño en las clasificatorias. Los herramientfanáticos esperan con ansias la competencia internacional.",
        authors=["Raúl Ortega"], date=datetime(2024, 1, 25), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/deportes/2024/02",
        url_normalized="https://cubadebate.cu/deportes/2024/02",
        title="Atletas cubanos ganan medallas en competencias",
        content="Atletas cubanos han ganado múltiples medallas en competencias internacionales de atletismo. Los deportistas han demostrado un alto nivel de preparación. Los entrenadores destacan el trabajo de las academias deportivas.",
        authors=["Diana Flores"], date=datetime(2024, 2, 6), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/deportes/2024/03",
        url_normalized="https://cubadebate.cu/deportes/2024/03",
        title="Boxeo cubano mantiene hegemonía regional",
        content="El boxeo cubano mantiene su hegemonía en los pugilados regionales. Los	boxeadores han conquistado oro en diversos torneos. Los expertos consideran que Cuba sigue siendo una potencia mundial del boxeo amateur.",
        authors=["Gustavo Peña"], date=datetime(2024, 2, 14), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/deportes/2024/04",
        url_normalized="https://cubadebate.cu/deportes/2024/04",
        title="Fútbol cubano mejora en ranking internacional",
        content="El fútbol cubano ha mejorado su posición en el ranking internacional de selecciones. El equipo nacional ha logrado victorias importantes en las últimas competencias. Los entrenadores trabajan en la formación de nuevos talentos.",
        authors=["Hugo Jiménez"], date=datetime(2024, 2, 22), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/deportes/2024/05",
        url_normalized="https://cubadebate.cu/deportes/2024/05",
        title="Juegos Centroamericanos serán en 2024",
        content="Los Juegos Centroamericanos y del Caribe se celebrarán en 2024. Los atletas cubanos se preparan intensamente para la competencia. Las autoridades deportivas han invertido en modernas instalaciones deportivas.",
        authors=["Marta Delgado"], date=datetime(2024, 3, 5), indexed=False, embeddings_generated=False
    ),
    
    # Cultura
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/cultura/2024/01",
        url_normalized="https://cubadebate.cu/cultura/2024/01",
        title="Festival de cine cubano atrae a visitantes",
        content="El festival de cine cubano ha atraído a miles de visitantes nacionales e internacionales. Se han proyectado películas de reconocidas directoras y directores. El evento promueve la cultura cinematográfica nacional.",
        authors=["Claudia Ruiz"], date=datetime(2024, 1, 28), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/cultura/2024/02",
        url_normalized="https://cubadebate.cu/cultura/2024/02",
        title="Artesanos cubanos exponen sus obras",
        content="Artesanos cubanos exponen sus obras en la feria internacional de artesanía. Los visitantes pueden adquirir piezas únicas de cerámica, tejidos y esculturas. La artesanía cubana es reconocida mundialmente por su calidad.",
        authors=["Fernando Soto"], date=datetime(2024, 2, 7), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/cultura/2024/03",
        url_normalized="https://cubadebate.cu/cultura/2024/03",
        title="Música tradicional cubana se mantiene viva",
        content="La música tradicional cubana se mantiene viva a través de grupos y escuelas de música. Los estudiantes aprenden los géneros auténticos como el son, la rumba y el mambo. Los artistas contemporáneos fusionan lo tradicional con lo moderno.",
        authors=["Rosa Vázquez"], date=datetime(2024, 2, 16), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/cultura/2024/04",
        url_normalized="https://cubadebate.cu/cultura/2024/04",
        title="Escritores cubanos publican nuevas novelas",
        content="Escritores cubanos han publicado nuevas novelas que están recibiendo elogios de la crítica literaria. Las obras abordan temas de la sociedad contemporánea. Las editoriales nacionales e internacionales han mostrado interés.",
        authors=["Alberto Romero"], date=datetime(2024, 2, 24), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/cultura/2024/05",
        url_normalized="https://cubadebate.cu/cultura/2024/05",
        title="Arquitectura histórica se preserva en La Habana",
        content="La arquitectura histórica de La Habana Vieja se preserva gracias a los esfuerzos de restauración. Edificios coloniales han sido recuperados para uso cultural y turístico. Los arquitectos trabajan en la conservación del patrimonio.",
        authors=["Gloria Ibarra"], date=datetime(2024, 3, 3), indexed=False, embeddings_generated=False
    ),
    
    # Tecnología
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/tecnologia/2024/01",
        url_normalized="https://cubadebate.cu/tecnologia/2024/01",
        title="Universidad cubana desarrolla software innovador",
        content="La universidad cubana ha desarrollado un software innovador para la gestión empresarial. El programa permite automatizar procesos y mejorar la eficiencia de las empresas. Los creadores han recibido reconocimientos nacionales.",
        authors=["Ricardo Peña"], date=datetime(2024, 1, 30), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/tecnologia/2024/02",
        url_normalized="https://cubadebate.cu/tecnologia/2024/02",
        title="Internet móvil se expande en el país",
        content="El internet móvil se está expandiendo en todo el territorio nacional. Más comunidades rurales tienen acceso a la red. Las autoridades trabajan para mejorar la conectividad y reducir los costos.",
        authors=["Sandra Mendoza"], date=datetime(2024, 2, 9), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/tecnologia/2024/03",
        url_normalized="https://cubadebate.cu/tecnologia/2024/03",
        title="Científicos crean aplicación para la agricultura",
        content="Científicos cubanos han creado una aplicación móvil para optimizar la agricultura. Los farmers pueden monitorear sus cultivos y recibir recomendaciones técnicas. La herramienta ha sido descargada por miles de usuarios.",
        authors=["Óscar Ramírez"], date=datetime(2024, 2, 17), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/tecnologia/2024/04",
        url_normalized="https://cubadebate.cu/tecnologia/2024/04",
        title="Red de universidades implementa e-learning",
        content="La red de universidades ha implementado plataformas de e-learning para la educación a distancia. Los estudiantes pueden acceder a cursos en línea desde cualquier lugar. La infraestructura tecnológica ha sido modernizada.",
        authors=["Verónica Luna"], date=datetime(2024, 2, 26), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/tecnologia/2024/05",
        url_normalized="https://cubadebate.cu/tecnologia/2024/05",
        title="Inteligencia artificial aplicada a la medicina",
        content="La inteligencia artificial se está aplicando en el campo de la medicina en Cuba. Los sistemas pueden diagnosticar enfermedades con alta precisión. Los investigadores trabajan en nuevos algoritmos para mejorar la atención médica.",
        authors=["Daniel Herrera"], date=datetime(2024, 3, 7), indexed=False, embeddings_generated=False
    ),
    
    # Medio Ambiente
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/medioambiente/2024/01",
        url_normalized="https://cubadebate.cu/medioambiente/2024/01",
        title="Reforestación en toda la isla",
        content="Un programa de reforestación se lleva a cabo en toda la isla. Se han plantado millones de árboles para recuperar áreas boscosas. Los voluntarios participan activamente en las jornadas de siembra.",
        authors=["Eugenio Guzmán"], date=datetime(2024, 2, 2), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/medioambiente/2024/02",
        url_normalized="https://cubadebate.cu/medioambiente/2024/02",
        title="Energías renovables en aumento",
        content="El uso de energías renovables está en aumento en el país. Se han instalado parques solares y eólicos en varias regiones. La transición energética contribuye a la reducción de emisiones de carbono.",
        authors=["Beatriz Pardo"], date=datetime(2024, 2, 11), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/medioambiente/2024/03",
        url_normalized="https://cubadebate.cu/medioambiente/2024/03",
        title="Protección de especies marinas en peligro",
        content="Se implementan medidas para la protección de especies marinas en peligro de extinción. Los santuario marinos han sido ampliados. Las autoridades trabajan con organizaciones internacionales para preservar la biodiversidad.",
        authors=["Francisco Leiva"], date=datetime(2024, 2, 19), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/medioambiente/2024/04",
        url_normalized="https://cubadebate.cu/medioambiente/2024/04",
        title="Cambio climático afecta la agricultura",
        content="El cambio climático está afectando la agricultura en diversas regiones del país. Los fenómenos meteorológicos extremos han causado pérdidas en las cosechas. Los científicos estudian estrategias de adaptación.",
        authors=["Isabel Bravo"], date=datetime(2024, 2, 27), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="cubadebate", url="https://cubadebate.cu/medioambiente/2024/05",
        url_normalized="https://cubadebate.cu/medioambiente/2024/05",
        title="Reciclaje se implementa en ciudades",
        content="Programas de reciclaje se están implementando en las principales ciudades del país. Los ciudadanos participan en la separación de residuos. Las autoridades han instalado puntos de acopio en neighborhoods.",
        authors=["Manuel Solís"], date=datetime(2024, 3, 8), indexed=False, embeddings_generated=False
    ),
    
    # Internacionales
    ScrapedDocument(
        source="telecentros", url="https://telecentros.cu/noticias/2024/01",
        url_normalized="https://telecentros.cu/noticias/2024/01",
        title="Cumbre mundial aborda crisis climática",
        content="Una cumbre mundial se reúne para abordar la crisis climática global. Líderes de países discuten acuerdos para reducir las emisiones de gases de efecto invernadero. Los activistas طلب more ambitious metas.",
        authors=["Teresa Arrieta"], date=datetime(2024, 1, 12), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="telecentros", url="https://telecentros.cu/noticias/2024/02",
        url_normalized="https://telecentros.cu/noticias/2024/02",
        title="Acuerdo comercial entre países latinoamericanos",
        content="Países latinoamericanos firman un nuevo acuerdo comercial para promover el intercambio de bienes y servicios. El pacto busca fortalecer la integración regional. Los empresarios esperan beneficiarse del mercado común.",
        authors=["Antonio Medina"], date=datetime(2024, 1, 19), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="telecentros", url="https://telecentros.cu/noticias/2024/03",
        url_normalized="https://telecentros.cu/noticias/2024/03",
        title="Conflicto internacional genera tensiones",
        content="Un conflicto internacional ha generado tensiones en diversas regiones del mundo. Las potencias mundiales discuten soluciones diplomáticas. Los efectos económicos se sienten en los mercados globales.",
        authors=["Carmen navarro"], date=datetime(2024, 2, 4), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="telecentros", url="https://telecentros.cu/noticias/2024/04",
        url_normalized="https://telecentros.cu/noticias/2024/04",
        title="Organismos internacionales aiden a países pobres",
        content="Organismos internacionales envían ayuda humanitaria a países que sufren crisis alimentarias. Los programas de asistencia incluyen alimentos, medicinas y agua potable. Millones de personas dependen de esta ayuda.",
        authors=["Roberto Castillo"], date=datetime(2024, 2, 13), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="telecentros", url="https://telecentros.cu/noticias/2024/05",
        url_normalized="https://telecentros.cu/noticias/2024/05",
        title="Migración masiva hacia países desarrollados",
        content="La migración masiva continúa hacia países desarrollados. Miles de personas buscan mejores oportunidades laborales y de vida. Los gobiernos debaten políticas migratorias más estrictas.",
        authors=["Patricia fuentes"], date=datetime(2024, 2, 21), indexed=False, embeddings_generated=False
    ),
    
    # Sociedad
    ScrapedDocument(
        source="radiorebelde", url="https://radiorebelde.cu/sociedad/2024/01",
        url_normalized="https://radiorebelde.cu/sociedad/2024/01",
        title="Educación universitaria es gratuita",
        content="La educación universitaria sigue siendo gratuita en el país. Miles de jóvenes acceden a la enseñanza superior cada año. Las universidades ofrecen carreras en diversas áreas del conocimiento.",
        authors=["JaimeEscobar"], date=datetime(2024, 1, 16), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="radiorebelde", url="https://radiorebelde.cu/sociedad/2024/02",
        url_normalized="https://radiorebelde.cu/sociedad/2024/02",
        title="Vivienda para familias de bajos recursos",
        content="El gobierno construye viviendas para familias de bajos recursos económicos. Los beneficiarios reciben casas con todas las comodidades básicas. El programa de vivienda ha mejorado la calidad de vida de miles de familias.",
        authors=["Margarita Duffy"], date=datetime(2024, 1, 26), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="radiorebelde", url="https://radiorebelde.cu/sociedad/2024/03",
        url_normalized="https://radiorebelde.cu/sociedad/2024/03",
        title="Seguridad social cubre a adultos mayores",
        content="El sistema de seguridad social cubre a los adultos mayores del país. Los pensionados reciben ayudas económicas mensuales. Los servicios de salud geriátrica han sido ampliados.",
        authors=["René Montoya"], date=datetime(2024, 2, 4), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="radiorebelde", url="https://radiorebelde.cu/sociedad/2024/04",
        url_normalized="https://radiorebelde.cu/sociedad/2024/04",
        title="Mujeres ocupan cargos de dirección",
        content="Las mujeres ocupan cada vez más cargos de dirección en la sociedad. Las políticas de igualdad de género han dado resultados positivos. Más mujeres líderes contribuyen al desarrollo del país.",
        authors=["Silvia Zambrano"], date=datetime(2024, 2, 23), indexed=False, embeddings_generated=False
    ),
    ScrapedDocument(
        source="radiorebelde", url="https://radiorebelde.cu/sociedad/2024/05",
        url_normalized="https://radiorebelde.cu/sociedad/2024/05",
        title="Juventud participa en programas sociales",
        content="La juventud participa activamente en programas sociales y comunitarios. Los estudiantes realizan actividades de voluntariado en neighborhoods marginados. Estas experiencias forman ciudadanos comprometidos.",
        authors=["Ernesto Páez"], date=datetime(2024, 3, 6), indexed=False, embeddings_generated=False
    ),
]
    
    await index_service.index_scraped_documents(scraped_docs)
    print("✅ Indexación completada")

if __name__ == "__main__":
    asyncio.run(main())
