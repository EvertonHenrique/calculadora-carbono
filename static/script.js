// ======================================================
// 🌱 Calculadora de Crédito de Carbono
// Autor: Uriel Rodrigues de Oliveira
// Versão aprimorada com créditos de carbono + gráfico colorido
// ======================================================

// Lista de perguntas
const perguntas = [
  { emoji: "💡", texto: "Quanto você consome de energia elétrica por mês (kWh)?", chave: "energia", anualizar: false },
  { emoji: "🚗", texto: "Quantos km você percorre por semana?", chave: "km", anualizar: true },
  { emoji: "🍖", texto: "Quantos kg de carne você consome por semana?", chave: "carne", anualizar: true },
  { emoji: "✈️", texto: "Quantas horas de voo você fez neste ano?", chave: "aviao", anualizar: false },
  { emoji: "🗑️", texto: "Quantos kg de lixo você gera por semana?", chave: "lixo", anualizar: true }
];

// Variáveis globais
let respostas = {};
let perguntaAtual = 0;

// Elementos do DOM
const perguntaContainer = document.getElementById("pergunta-container");
const resultadoContainer = document.getElementById("resultado-container");
const btnProximo = document.getElementById("btn-proximo");

// Função para exibir perguntas
function mostrarPergunta() {
  if (perguntaAtual >= perguntas.length) {
    enviarRespostas();
    return;
  }

  const p = perguntas[perguntaAtual];
  perguntaContainer.innerHTML = `
    <div class="fadeIn">
      <h3>${p.emoji} ${p.texto}</h3>
      ${p.chave === "km" ? `
        <label>Selecione o transporte principal:</label><br>
        <select id="tipoTransporte">
          <option value="carro">🚙 Carro</option>
          <option value="moto">🏍️ Moto</option>
          <option value="onibus">🚌 Ônibus</option>
          <option value="metro">🚆 Metrô/Trem</option>
          <option value="bike">🚲 Bicicleta</option>
          <option value="caminhada">🚶 Caminhada</option>
        </select><br>
      ` : ""}
      <input id="entrada" type="number" step="any" placeholder="Digite um valor positivo" />
    </div>
  `;
}

// Avança para a próxima pergunta
btnProximo.addEventListener("click", () => {
  const entrada = document.getElementById("entrada");
  const p = perguntas[perguntaAtual];

  if (!entrada || entrada.value.trim() === "") {
    exibirAlerta("⚠️ Por favor, insira um valor numérico antes de continuar.");
    return;
  }

  const valor = parseFloat(entrada.value);
  if (isNaN(valor) || valor < 0) {
    exibirAlerta("🚫 Valor inválido. Digite um número positivo.");
    return;
  }

  let resposta = valor;
  if (p.anualizar) resposta *= 52;
  respostas[p.chave] = resposta;

  if (p.chave === "km") {
    const tipoSelect = document.getElementById("tipoTransporte");
    respostas["tipo"] = tipoSelect ? tipoSelect.value : "carro";
  }

  perguntaAtual++;
  mostrarPergunta();
});

// Envia dados ao backend Flask
async function enviarRespostas() {
  try {
    exibirLoader(true);
    const resp = await fetch("/calcular", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(respostas)
    });

    if (!resp.ok) throw new Error("Erro ao conectar com o servidor.");
    const data = await resp.json();
    exibirLoader(false);
    mostrarResultado(data);
  } catch (erro) {
    exibirLoader(false);
    exibirAlerta("❌ Ocorreu um erro: " + erro.message);
  }
}

// Mostra resultado final com gráfico e botões
function mostrarResultado(data) {
  perguntaContainer.style.display = "none";
  btnProximo.style.display = "none";
  resultadoContainer.style.display = "block";

  // 💰 Cálculo de créditos e custo total
  const creditoCarbono = data.total_toneladas; // 1 crédito = 1 tonelada
  const precoMedio = Object.values(data.compensacoes).reduce((a, b) => a + b, 0) / Object.keys(data.compensacoes).length;
  const custoTotal = (creditoCarbono * precoMedio).toFixed(2);

  resultadoContainer.innerHTML = `
    <h3>🌍 Resultado Final</h3>
    <p>Você emite aproximadamente <b>${data.total_toneladas}</b> toneladas de CO₂e por ano.</p>
    <p>Isso equivale a <b>${creditoCarbono.toFixed(2)}</b> créditos de carbono 🌿</p>
    <p>Ou seja, seria necessário plantar <b>${data.arvores}</b> árvores 🌳 para compensar.</p>
    <h4>💰 Custo estimado de compensação:</h4>
    <p><b>R$ ${custoTotal}</b></p>
    <h4>📊 Distribuição das Emissões:</h4>
    <canvas id="graficoPizza" width="400" height="400"></canvas>
    <div class="botoes-finais">
      <button id="btn-recalcular">🔄 Recalcular</button>
      <button id="btn-relatorio">🧾 Gerar Relatório</button>
    </div>
  `;

  desenharGrafico(data.categorias);
  document.getElementById("btn-recalcular").addEventListener("click", reiniciarQuiz);
  document.getElementById("btn-relatorio").addEventListener("click", () => gerarRelatorio(data));
}

// 🎨 Gráfico colorido por categoria
function desenharGrafico(categorias) {
  const ctx = document.getElementById("graficoPizza").getContext("2d");

  const coresPorCategoria = {
    Energia: "#ffb300",    // amarelo
    Transporte: "#1976d2", // azul
    Alimentação: "#d32f2f",// vermelho
    Viagens: "#9c27b0",    // roxo
    Resíduos: "#4caf50"    // verde
  };

  new Chart(ctx, {
    type: "pie",
    data: {
      labels: Object.keys(categorias),
      datasets: [{
        data: Object.values(categorias),
        backgroundColor: Object.keys(categorias).map(k => coresPorCategoria[k] || "#81c784"),
        borderColor: "#fff",
        borderWidth: 2,
      }]
    },
    options: {
      plugins: {
        legend: { position: "bottom", labels: { color: "#1b5e20", font: { size: 14 } } },
        tooltip: {
          backgroundColor: "#2e7d32",
          titleColor: "#fff",
          bodyColor: "#fff",
          callbacks: {
            label: (context) => `${context.label}: ${context.parsed.toFixed(1)} kg CO₂e`
          }
        }
      },
      animation: { animateRotate: true, duration: 1600 }
    }
  });
}

// Reinicia o quiz
function reiniciarQuiz() {
  respostas = {};
  perguntaAtual = 0;
  resultadoContainer.style.display = "none";
  perguntaContainer.style.display = "block";
  btnProximo.style.display = "inline-block";
  mostrarPergunta();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Gera relatório em nova aba
function gerarRelatorio(data) {
  const novaJanela = window.open("", "_blank");
  const creditoCarbono = data.total_toneladas;
  novaJanela.document.write(`
    <html>
    <head><title>Relatório de Emissões</title></head>
    <body style="font-family:Arial; background:#f5f5f5; padding:20px;">
      <h2>🌍 Relatório de Emissões</h2>
      <p><b>Total:</b> ${data.total_toneladas} toneladas CO₂e/ano</p>
      <p><b>Créditos de Carbono:</b> ${creditoCarbono.toFixed(2)} créditos</p>
      <p><b>Árvores necessárias:</b> ${data.arvores}</p>
      <h3>Distribuição:</h3>
      <ul>${Object.entries(data.categorias).map(([k, v]) => `<li>${k}: ${v.toFixed(1)} kg CO₂e</li>`).join("")}</ul>
      <h3>Custos de Compensação:</h3>
      <ul>${Object.entries(data.compensacoes).map(([k, v]) => `<li>${k}: R$ ${v.toFixed(2)}</li>`).join("")}</ul>
      <p style="margin-top:30px; color:gray;">Gerado por Uriel Rodrigues de Oliveira — APS IPE © 2025</p>
    </body>
    </html>
  `);
  novaJanela.document.close();
  novaJanela.print();
}

// Alerta visual
function exibirAlerta(mensagem) {
  const aviso = document.createElement("div");
  aviso.textContent = mensagem;
  Object.assign(aviso.style, {
    position: "fixed",
    bottom: "25px",
    left: "50%",
    transform: "translateX(-50%)",
    background: "#4caf50",
    color: "#fff",
    padding: "10px 20px",
    borderRadius: "10px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
    zIndex: "1000",
    opacity: "0",
    transition: "opacity 0.5s"
  });
  document.body.appendChild(aviso);
  setTimeout(() => aviso.style.opacity = "1", 100);
  setTimeout(() => aviso.style.opacity = "0", 2500);
  setTimeout(() => aviso.remove(), 3000);
}

// Loader visual
function exibirLoader(mostrar) {
  if (mostrar) {
    resultadoContainer.innerHTML = `
      <div style="text-align:center; margin:40px;">
        <div class="loader" style="
          border: 6px solid #c8e6c9;
          border-top: 6px solid #4caf50;
          border-radius: 50%;
          width: 50px;
          height: 50px;
          margin: 0 auto 15px auto;
          animation: spin 1s linear infinite;
        "></div>
        <p>Calculando emissões... 🌿</p>
      </div>
    `;
  }
}

mostrarPergunta();

const estilo = document.createElement("style");
estilo.innerHTML = `
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.fadeIn { animation: fadeIn 0.6s ease-in-out; }
`;
document.head.appendChild(estilo);
