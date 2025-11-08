// -----------------------------------------------------------
// 🌱 Calculadora de Crédito de Carbono - Uriel Rodrigues de Oliveira
// -----------------------------------------------------------

const perguntas = [
  { emoji: "💡", texto: "Quanto você consome de energia elétrica por mês (kWh)?", chave: "energia", anualizar: false },
  { emoji: "🚗", texto: "Quantos km você percorre por semana?", chave: "km", anualizar: true },
  { emoji: "🍖", texto: "Quantos kg de carne você consome por semana?", chave: "carne", anualizar: true },
  { emoji: "✈️", texto: "Quantas horas de voo você fez neste ano?", chave: "aviao", anualizar: false },
  { emoji: "🗑️", texto: "Quantos kg de lixo você gera por semana?", chave: "lixo", anualizar: true }
];

let respostas = {};
let perguntaAtual = 0;

const perguntaContainer = document.getElementById("pergunta-container");
const resultadoContainer = document.getElementById("resultado-container");
const btnProximo = document.getElementById("btn-proximo");

// -----------------------------------------------------------
// Exibe a pergunta atual ao usuário
// -----------------------------------------------------------
function mostrarPergunta() {
  if (perguntaAtual >= perguntas.length) {
    enviarRespostas();
    return;
  }

  const p = perguntas[perguntaAtual];
  perguntaContainer.innerHTML = `
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
  `;
}

// -----------------------------------------------------------
// Avança para a próxima pergunta
// -----------------------------------------------------------
btnProximo.addEventListener("click", () => {
  const entrada = document.getElementById("entrada");
  const p = perguntas[perguntaAtual];

  if (!entrada || entrada.value.trim() === "") {
    alert("⚠️ Por favor, insira um valor numérico antes de continuar.");
    return;
  }

  const valor = parseFloat(entrada.value);
  if (isNaN(valor) || valor < 0) {
    alert("🚫 Valor inválido. Digite um número positivo.");
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

// -----------------------------------------------------------
// Envia as respostas para o backend em Flask
// -----------------------------------------------------------
async function enviarRespostas() {
  try {
    const resp = await fetch("/calcular", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(respostas)
    });

    if (!resp.ok) throw new Error("Erro na resposta do servidor.");

    const data = await resp.json();

    if (data.erro) {
      alert("⚠️ " + data.erro);
      return;
    }

    mostrarResultado(data);
  } catch (erro) {
    alert("❌ Ocorreu um problema ao calcular. Tente novamente.\nDetalhes: " + erro.message);
  }
}

// -----------------------------------------------------------
// Exibe o resultado final
// -----------------------------------------------------------
function mostrarResultado(data) {
  perguntaContainer.style.display = "none";
  btnProximo.style.display = "none";
  resultadoContainer.style.display = "block";

  let html = `
    <h3>🌍 Resultado Final</h3>
    <p>Você emite aproximadamente <b>${data.total_toneladas}</b> toneladas de CO₂e por ano.</p>
    <p>Isso equivale a plantar <b>${data.arvores}</b> árvores 🌳</p>
    <h4>💰 Custos de Compensação:</h4>
    <ul>
  `;

  for (const [nome, preco] of Object.entries(data.compensacoes)) {
    html += `<li>${nome}: R$ ${preco.toFixed(2)}</li>`;
  }

  html += "</ul><h4>📊 Distribuição das Emissões:</h4><div id='grafico'></div>";
  resultadoContainer.innerHTML = html;

  // Mostra o gráfico
  desenharGrafico(data.categorias);

  // Botão: Gerar Relatório
  const btnRelatorio = document.createElement("button");
  btnRelatorio.textContent = "📄 Gerar Relatório";
  btnRelatorio.onclick = () => gerarRelatorio(data);
  resultadoContainer.appendChild(btnRelatorio);

  // Botão: Recalcular
  const btnRecalcular = document.createElement("button");
  btnRecalcular.textContent = "🔄 Recalcular";
  btnRecalcular.onclick = () => reiniciarQuiz();
  resultadoContainer.appendChild(btnRecalcular);
}

// -----------------------------------------------------------
// 🥧 Gráfico de Pizza (SVG puro, sem bibliotecas externas)
// -----------------------------------------------------------
function desenharGrafico(categorias) {
  const total = Object.values(categorias).reduce((a, b) => a + b, 0);
  let anguloInicial = 0;
  const raio = 100;
  const cores = ["#4caf50", "#81c784", "#66bb6a", "#388e3c", "#2e7d32"];
  let setores = "";
  let legendas = "";
  let i = 0;

  for (const [categoria, valor] of Object.entries(categorias)) {
    const proporcao = valor / total;
    const anguloFinal = anguloInicial + proporcao * 2 * Math.PI;

    const x1 = 100 + raio * Math.cos(anguloInicial);
    const y1 = 100 + raio * Math.sin(anguloInicial);
    const x2 = 100 + raio * Math.cos(anguloFinal);
    const y2 = 100 + raio * Math.sin(anguloFinal);

    const grandeArco = proporcao > 0.5 ? 1 : 0;

    setores += `
      <path d="M100,100 L${x1},${y1} A${raio},${raio} 0 ${grandeArco},1 ${x2},${y2} Z" fill="${cores[i % cores.length]}" />
    `;

    legendas += `
      <div style="display:flex; align-items:center; gap:5px; font-size:14px;">
        <div style="width:15px; height:15px; background:${cores[i % cores.length]}; border-radius:3px;"></div>
        <span>${categoria}: ${(proporcao * 100).toFixed(1)}%</span>
      </div>
    `;

    anguloInicial = anguloFinal;
    i++;
  }

  document.getElementById("grafico").innerHTML = `
    <div style="display:flex; flex-direction:column; align-items:center;">
      <svg width="220" height="220" viewBox="0 0 200 200">${setores}</svg>
      <div style="margin-top:10px;">${legendas}</div>
    </div>
  `;
}

// -----------------------------------------------------------
// 🧾 Gera um relatório simples em HTML (impressão ou PDF)
// -----------------------------------------------------------
function gerarRelatorio(data) {
  const novaJanela = window.open("", "_blank");
  novaJanela.document.write(`
    <html>
    <head>
      <title>Relatório de Emissões - Crédito de Carbono</title>
      <style>
        body { font-family: Arial; background: #f5f5f5; padding: 20px; color: #1b5e20; }
        h1, h2 { text-align: center; color: #2e7d32; }
        .box { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); margin-bottom: 15px; }
        ul { list-style: none; padding: 0; }
        li { margin: 5px 0; }
        .rodape { text-align: center; margin-top: 30px; font-size: 14px; color: gray; }
      </style>
    </head>
    <body>
      <h1>🌍 Relatório de Emissões de Carbono</h1>
      <div class="box">
        <h2>Resumo</h2>
        <p><b>Total de emissões:</b> ${data.total_toneladas} toneladas de CO₂e/ano</p>
        <p><b>Árvores necessárias:</b> ${data.arvores}</p>
      </div>

      <div class="box">
        <h2>Distribuição das Emissões</h2>
        <ul>
          ${Object.entries(data.categorias).map(([k, v]) => `<li>${k}: ${v.toFixed(1)} kg CO₂e</li>`).join("")}
        </ul>
      </div>

      <div class="box">
        <h2>Custos de Compensação</h2>
        <ul>
          ${Object.entries(data.compensacoes).map(([k, v]) => `<li>${k}: R$ ${v.toFixed(2)}</li>`).join("")}
        </ul>
      </div>

      <p class="rodape">Gerado automaticamente por Uriel Rodrigues de Oliveira — Projeto APS IPE © 2025</p>
    </body>
    </html>
  `);
  novaJanela.document.close();
  novaJanela.print();
}

// -----------------------------------------------------------
// 🔁 Reinicia o quiz para novo cálculo
// -----------------------------------------------------------
function reiniciarQuiz() {
  respostas = {};
  perguntaAtual = 0;
  resultadoContainer.style.display = "none";
  perguntaContainer.style.display = "block";
  btnProximo.style.display = "inline-block";
  mostrarPergunta();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Inicializa o quiz
mostrarPergunta();
