#  Arquitetura Serverless para API REST de Gestão de Pedidos

> **AVISO IMPORTANTE:** Conforme as boas práticas de **FinOps** e gerenciamento de custos, todos os recursos desta arquitetura na AWS (API Gateway, AWS Lambda, DynamoDB e CloudWatch) foram **desativados/desligados** após a conclusão do projeto acadêmico para evitar cobranças por recursos ociosos. Portanto, os endpoints originais não estão operacionais para testes públicos no momento. O código e os passos de implantação abaixo servem como documentação e guia para reprodução integral da infraestrutura.

---

##  Descrição do Projeto
Este projeto apresenta o desenvolvimento e a implantação de uma solução 100% serverless na nuvem Amazon Web Services (AWS) voltada para o gerenciamento de pedidos de uma plataforma de e-commerce. A proposta moderniza os sistemas tradicionais (geralmente baseados em servidores ligados 24/7) ao adotar componentes de computação sob demanda, garantindo alta escalabilidade automática, custo proporcional ao uso e facilidade de manutenção.

A API é capaz de realizar com eficiência o fluxo de CRUD e controle de estados de pedidos: cadastro, listagem, consulta por ID, substituição integral, atualização parcial e cancelamento/remoção.


##  Arquitetura da Solução
A arquitetura foi desenhada seguindo o fluxo abaixo:

1. **Cliente / Postman:** Realiza requisições HTTP para interagir com o sistema.
2. **Amazon API Gateway:** Gerencia com segurança o roteamento de entrada HTTP e conecta as rotas diretamente às funções de computação.
3. **AWS Lambda:** Executa a lógica de negócios sob demanda (como validação de status e cálculo de valores totais de forma automática).
4. **Amazon DynamoDB:** Banco de dados NoSQL responsável pela persistência rápida e de alta performance dos dados dos pedidos.
5. **Amazon CloudWatch:** Centraliza logs, métricas operacionais, dashboards visuais e alertas de falha do ecossistema.

---

##  Tecnologias e Serviços Utilizados
* **AWS Lambda:** Execução de código em ambiente serverless isolado.
* **Amazon API Gateway:** Criação e publicação de APIs REST / HTTP seguras e escaláveis.
* **Amazon DynamoDB:** Armazenamento chave-valor NoSQL totalmente gerenciado.
* **Amazon CloudWatch:** Ferramenta para monitoramento, geração de métricas e observabilidade.
* **AWS CloudShell / AWS CLI:** Interface de linha de comando utilizada para a automação e criação da infraestrutura.

---

##  Estrutura de Endpoints Implementados
A API gerencia as requisições por meio das seguintes rotas configuradas no API Gateway (atualmente pausadas):

* `POST /pedidos` - Cadastro de um novo pedido (com cálculo automático do valor total e validação de status inicial).
* `GET /pedidos` - Listagem geral de todos os pedidos armazenados.
* `GET /pedidos/{id}` - Consulta detalhada de um pedido específico por ID.
* `PUT /pedidos/{id}` - Substituição/Atualização completa dos dados do pedido.
* `PATCH /pedidos/{id}` - Atualização parcial de atributos específicos do pedido.
* `DELETE /pedidos/{id}` - Remoção ou cancelamento lógico do pedido.

---
