O projeto visa a clonagem de páginas web, permitindo copiar e recriar o conteúdo de sites de maneira automatizada. Utilizando bibliotecas como requests e BeautifulSoup,
o projeto extrai dados estáticos das páginas, como textos, imagens e links. Para páginas dinâmicas que exigem interações, o Selenium é empregado para navegar e capturar conteúdo interativo.
O uso de aiohttp acelera o processo de coleta de dados assíncrona, enquanto zipfile e shutil são utilizados para manipulação de arquivos, permitindo a extração e organização de conteúdos clonados.
A biblioteca tqdm oferece uma barra de progresso para monitorar o andamento da clonagem de páginas. O objetivo é criar uma réplica funcional de uma página web, preservando a estrutura e o conteúdo original.


The project focuses on web page cloning, allowing for the automated copying and recreation of website content. Using libraries like requests and BeautifulSoup,
the project extracts static data from pages, such as text, images, and links. For dynamic pages that require interaction, Selenium is used to navigate and capture interactive content.
The use of aiohttp speeds up the asynchronous data collection process, while zipfile and shutil are employed for file manipulation, enabling the extraction and organization of cloned content.
The tqdm library provides a progress bar to track the cloning process. The goal is to create a functional replica of a web page, preserving the original structure and content.
