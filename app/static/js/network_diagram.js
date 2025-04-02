document.addEventListener('DOMContentLoaded', function() {
    const networkDiagram = document.getElementById('network-diagram');
    let devices = [];
    let svg, simulation;
    let zoom = d3.zoom()
        .scaleExtent([0.5, 3])
        .on('zoom', (event) => {
            svg.select('g').attr('transform', event.transform);
        });

    // Función para cargar dispositivos de ejemplo
    function loadSampleDevices() {
        devices = [
            { id: 1, name: 'Router', type: 'router', ip: '192.168.1.1' },
            { id: 2, name: 'PC1', type: 'device', ip: '192.168.1.2' },
            { id: 3, name: 'PC2', type: 'device', ip: '192.168.1.3' },
            { id: 4, name: 'Server1', type: 'device', ip: '192.168.1.4' },
            { id: 5, name: 'Server2', type: 'device', ip: '192.168.1.5' }
        ];
        renderNetworkDiagram();
    }

    function renderNetworkDiagram() {
        const containerWidth = networkDiagram.clientWidth;
        const containerHeight = networkDiagram.clientHeight;
        networkDiagram.innerHTML = '';

        svg = d3.select(networkDiagram)
            .append('svg')
            .attr('width', containerWidth)
            .attr('height', containerHeight)
            .call(zoom);

        const g = svg.append('g');

        // Prepara nodos y enlaces
        const nodes = devices.map(d => Object.assign({}, d));
        let links = [];
        const routerIndex = devices.findIndex(d => d.type === 'router');
        if (routerIndex !== -1) {
            devices.forEach((d, i) => {
                if (i !== routerIndex) {
                    links.push({ source: routerIndex, target: i });
                }
            });
        }

        simulation = d3.forceSimulation(nodes)
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(containerWidth / 2, containerHeight / 2))
            .force("link", d3.forceLink(links).distance(150).strength(1))
            .force("collision", d3.forceCollide().radius(50));

        const link = g.selectAll("line")
            .data(links)
            .enter()
            .append("line")
            .attr("class", "connection-line");

        const node = g.selectAll("circle")
            .data(nodes)
            .enter()
            .append("circle")
            .attr("class", "device-node")
            .attr("r", d => d.type === 'router' ? 20 : 15)
            .attr("fill", d => d.type === 'router' ? "#ff6b6b" : "#4ecdc4")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        // Agregar etiquetas de texto
        const labels = g.selectAll("text")
            .data(nodes)
            .enter()
            .append("text")
            .attr("class", "device-label")
            .text(d => `${d.name}\n${d.ip}`)
            .attr("dy", 25);

        simulation.on("tick", () => {
            link.attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            node.attr("cx", d => d.x)
                .attr("cy", d => d.y);
            labels.attr("x", d => d.x)
                  .attr("y", d => d.y);
        });

        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
    }

    // Controles de zoom
    document.getElementById('zoomIn').addEventListener('click', () => {
        svg.transition().duration(300).call(zoom.scaleBy, 1.2);
    });

    document.getElementById('zoomOut').addEventListener('click', () => {
        svg.transition().duration(300).call(zoom.scaleBy, 0.8);
    });

    document.getElementById('zoomReset').addEventListener('click', () => {
        svg.transition().duration(300).call(zoom.transform, d3.zoomIdentity);
    });

    // Cargar datos de ejemplo al inicio
    loadSampleDevices();
}); 