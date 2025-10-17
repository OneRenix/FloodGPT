tailwind.config = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
}

function toggleAccordion(btn) {
  const content = btn.nextElementSibling;
  const icon = btn.querySelector("i");
  content.classList.toggle("hidden");
  icon.style.transform = content.classList.contains('hidden') ? 'rotate(0deg)' : 'rotate(180deg)';
}
lucide.createIcons();

function shortenLabel(label, maxLength = 20) {
  if (typeof label !== 'string') return label;
  if (label.length > maxLength) {
    return label.substring(0, maxLength) + '...';
  }
  return label;
}

function setSampleQuery(text){
  document.getElementById('query-input').value = text.trim();
  document.getElementById('guided-queries-modal').classList.add('hidden');
}

function openTab(evt, tabName) {
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.add('hidden');
  });
  document.querySelectorAll('.tab-button').forEach(btn => {
    btn.classList.remove('active', 'text-white', 'border-[#0BA6DF]', 'border-b-2');
    btn.classList.add('text-gray-400', 'border-transparent');
  });
  
  const tabContent = document.getElementById(tabName);
  if (tabContent) {
    tabContent.classList.remove('hidden');
  }
  
  const tabButton = evt ? evt.currentTarget : document.querySelector(`[onclick="openTab(event, '${tabName}')"]`);
  if (tabButton) {
    tabButton.classList.add('active', 'text-white', 'border-b-2', 'border-[#0BA6DF]');
    tabButton.classList.remove('text-gray-400', 'border-transparent');
  }
}

function renderDataTable(dfData) {
  if ($.fn.DataTable.isDataTable('#results-table')) {
    $('#results-table').DataTable().destroy();
    $('#results-table').empty();
  }

  if (!dfData || !dfData.columns || !dfData.data || dfData.data.length === 0) {
    $('#results-table').html('<thead><tr><th class="text-gray-400">No data to display.</th></tr></thead>');
    return;
  }

  const columns = dfData.columns.map(col => ({ title: col }));
  
  // Check for numeric columns to apply formatting
  const columnDefs = [];
  dfData.data[0].forEach((cell, index) => {
    if (typeof cell === 'number') {
      columnDefs.push({
        targets: index,
        render: function (data, type, row) {
          if (type === 'display' && data !== null) {
            return data.toLocaleString('en-US');
          }
          return data;
        }
      });
    }
  });

  new DataTable('#results-table', {
    data: dfData.data,
    columns: columns,
    columnDefs: columnDefs,
    responsive: true,
    layout: {
        topStart: 'pageLength',
        topEnd: 'search',
        bottomStart: 'info',
        bottomEnd: 'paging'
    }
  });
}

function resetResults() {
  document.getElementById('sql-query').textContent = "";
  if ($.fn.DataTable.isDataTable('#results-table')) {
    $('#results-table').DataTable().destroy();
    $('#results-table').empty();
  }
  document.getElementById('viz-rec').textContent = "";
  document.getElementById('chart-json').textContent = "";
  document.getElementById('plotly-chart').innerHTML = "<p class='text-gray-400 mt-20 text-center'>No chart yet.</p>";
  document.getElementById('explain-content').textContent = "";
}

function submitQuery() {
  const question = document.getElementById('query-input').value;
  if (!question.trim()) {
    alert('Please enter a question.');
    return;
  }

  document.getElementById('loading-overlay').classList.remove('hidden');

  grecaptcha.ready(function() {
    grecaptcha.execute('6LfrwuwrAAAAAM33Dc6V2ua5Z2xk90VmGTh1zIZV', {
      action: 'submit'
    }).then(function(token) {
      document.getElementById('recaptcha-token').value = token;
      const honeypot = document.querySelector('[name="email_confirm"]').value;

      resetResults();
      localStorage.setItem("pendingQuery", question);
      localStorage.setItem("recaptchaToken", token);
      localStorage.setItem("honeypot", honeypot);

      setTimeout(() => {
        window.location.reload(true);
      }, 300);
    });
  });
}

function runPendingQuery() {
  const pending = localStorage.getItem("pendingQuery");
  if (pending && pending.trim() !== "") {
    document.getElementById('query-input').value = pending;
    const token = localStorage.getItem("recaptchaToken");
    const honeypot = localStorage.getItem("honeypot");
    localStorage.removeItem("pendingQuery");
    localStorage.removeItem("recaptchaToken");
    localStorage.removeItem("honeypot");
    runAgent(pending, token, honeypot);
  }
}

function runAgent(question, token, honeypot) {
  const statusDiv = document.getElementById('status');
  const submitBtn = document.getElementById('submit-btn');
  const loadingOverlay = document.getElementById('loading-overlay');

  submitBtn.disabled = true;
  submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
  loadingOverlay.classList.remove('hidden');
  statusDiv.textContent = 'Agent is thinking...';

  fetch('/stream-agent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: question,
        recaptcha_token: token,
        honeypot: honeypot
      }),
    })
    .then(response => {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      function push() {
        reader.read().then(({
          done,
          value
        }) => {
          if (done) {
            statusDiv.textContent = 'Done!';
            submitBtn.disabled = false;
            submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            loadingOverlay.classList.add('hidden');
            return;
          }
          const chunk = decoder.decode(value, {
            stream: true
          });
          const lines = chunk.split('\n');
          for (const line of lines) {
            if (line.startsWith('data:')) {
              const eventData = line.substring(5).trim();
              if (eventData) {
                const resultsTabs = document.getElementById('results-tabs');
                if (resultsTabs.classList.contains('hidden')) {
                  resultsTabs.classList.remove('hidden');
                  openTab(null, 'explain-tab');
                }

                const parsedEvent = JSON.parse(eventData);
                const { 
                  event: nodeName, 
                  data: nodeOutput 
                } = parsedEvent;

                if (nodeName === 'validate_question' && nodeOutput.error === 'Unsupported question') {
                  statusDiv.textContent = 'Your question is not supported. Please ask questions related to flood control projects.';
                  submitBtn.disabled = false;
                  submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                  loadingOverlay.classList.add('hidden');
                  return;
                }
                 if (nodeName === 'validate_question' && nodeOutput.error) {
                    statusDiv.textContent = nodeOutput.error;
                    submitBtn.disabled = false;
                    submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                    loadingOverlay.classList.add('hidden');
                    return;
                }

                if (nodeName === 'validate_sql') {
                  statusDiv.textContent = 'SQL validated. Executing...';
                  document.getElementById('sql-query').textContent = nodeOutput.validated_sql;
                } else if (nodeName === 'execute_sql') {
                  statusDiv.textContent = 'Query executed. Recommending visualization...';
                  renderDataTable(nodeOutput.sql_dataframe);
                } else if (nodeName === 'visualizer') {
                  statusDiv.textContent = 'Recommendation received. Formatting data...';
                  document.getElementById('viz-rec').textContent = `Recommended Chart Type: ${nodeOutput.visualization}`;
                } else if (nodeName === 'formatter') {
                  statusDiv.textContent = 'Process complete!';
                  document.getElementById('chart-json').textContent = JSON.stringify(nodeOutput.formatted_data_for_visualization, null, 2);
                  renderPlotly(nodeOutput);
                } else if (nodeName === 'insight') {
                  statusDiv.textContent = 'Generating insights...';
                  const converter = new showdown.Converter();
                  const html = converter.makeHtml(nodeOutput.insight);
                  document.getElementById('explain-content').innerHTML = html;
                  openTab(null, 'explain-tab');
                } else if (nodeName === 'end' || nodeName === 'error') {
                  statusDiv.textContent = nodeName === 'error' ? `An error occurred: ${nodeOutput}` : 'Done!';
                  submitBtn.disabled = false;
                  submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                  loadingOverlay.classList.add('hidden');
                  return;
                }
              }
            }
          }
          push();
        });
      }
      push();
    })
    .catch(err => {
      statusDiv.textContent = 'Connection to server failed.';
      submitBtn.disabled = false;
      submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
      loadingOverlay.classList.add('hidden');
    });
}

function renderPlotly(chartJsonWrapper){
  let chartJson = chartJsonWrapper?.formatted_data_for_visualization || chartJsonWrapper;
  if(chartJson.formatted_data_for_visualization) chartJson = chartJson.formatted_data_for_visualization;
  
  let type = (chartJson.type || 'none').toLowerCase();
  let orientation = 'v';

  if(type === 'none'){
    document.getElementById('plotly-chart').innerHTML="<p class='text-gray-400 text-center mt-20'>No visualization available.</p>";
    return;
  }
  if(type === 'horizontal_bar'){
    type = 'bar'; 
    orientation = 'h';
  }
  if(!chartJson.data || !Array.isArray(chartJson.data.labels) || !Array.isArray(chartJson.data.values)){
    document.getElementById('plotly-chart').innerHTML="<p class='text-red-400 text-center mt-20'>Invalid chart data format.</p>"; 
    return;
  }

  let traces = [];
  const colors = ['#4285F4', '#DB4437', '#F4B400', '#0F9D58', '#AB47BC', '#00ACC1', '#FF7043', '#9E9D24', '#5C6BC0', '#8E24AA'];
  
  if (chartJson.data.labels) {
    chartJson.data.labels = chartJson.data.labels.map(label => shortenLabel(label));
  }

  if(type === 'pie'){
    traces = [{
      labels: chartJson.data.labels,
      values: chartJson.data.values[0].data,
      type: 'pie',
      textinfo: 'label+percent',
      marker: { colors: colors },
      hoverinfo: 'label+percent+value'
    }];
  } else {
    chartJson.data.values.forEach((series, idx) => { 
      const trace = {
        x: orientation === 'v' ? chartJson.data.labels : series.data,
        y: orientation === 'v' ? series.data : chartJson.data.labels,
        name: series.label || `Series ${idx+1}`,
        type: type,
        orientation: orientation,
        marker: { color: colors[idx % colors.length] }
      };
      traces.push(trace);
    });
  }

  const layout = {
    title: {
      text: chartJson.options?.title || '',
      font: { color: '#e5e7eb', size: 18 }
    },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#d1d5db' },
    xaxis: { gridcolor: 'rgba(255,255,255,0.1)', zerolinecolor: 'rgba(255,255,255,0.2)' },
    yaxis: { gridcolor: 'rgba(255,255,255,0.1)', zerolinecolor: 'rgba(255,255,255,0.2)' },
    margin: {
      l: 150,
      r: 50,
      b: 150,
      t: 50,
      pad: 4
    }
  };

  try {
    Plotly.react('plotly-chart', traces, layout, {responsive: true, displayModeBar: false});
  } catch(err) {
    document.getElementById('plotly-chart').innerHTML=`<p class='text-red-400 text-center mt-20'>Error rendering chart: ${err}</p>`;
  }
}

// Initial setup
document.addEventListener('DOMContentLoaded', () => {
  runPendingQuery();

  const guidedQueriesBtn = document.getElementById('guided-queries-btn');
  const closeModalBtn = document.getElementById('close-modal-btn');
  const modal = document.getElementById('guided-queries-modal');

  guidedQueriesBtn.addEventListener('click', () => {
    modal.classList.remove('hidden');
  });

  closeModalBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
  });

  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.classList.add('hidden');
    }
  });
});