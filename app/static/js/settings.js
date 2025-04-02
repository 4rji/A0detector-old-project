document.addEventListener('DOMContentLoaded', function() {
    // Cargar subredes existentes
    loadSubnets();
    
    // Manejar envío del formulario de subredes
    document.getElementById('subnet-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const subnetInput = document.getElementById('subnet-input');
        const subnet = subnetInput.value.trim();
        
        if (validateSubnet(subnet)) {
            addSubnet(subnet);
            subnetInput.value = '';
        } else {
            alert('Por favor ingrese una subred válida (ejemplo: 192.168.1)');
        }
    });
});

function validateSubnet(subnet) {
    // Validar formato de subred (xxx.xxx.xxx)
    const pattern = /^(\d{1,3}\.){2}\d{1,3}$/;
    if (!pattern.test(subnet)) return false;
    
    // Validar que cada número esté entre 0 y 255
    const parts = subnet.split('.');
    return parts.every(part => {
        const num = parseInt(part);
        return num >= 0 && num <= 255;
    });
}

function loadSubnets() {
    fetch('/dashboard/settings/subnets')
        .then(response => response.json())
        .then(data => {
            const subnetList = document.getElementById('subnet-list');
            subnetList.innerHTML = '';
            
            data.subnets.forEach(subnet => {
                addSubnetToList(subnet);
            });
        })
        .catch(error => {
            console.error('Error loading subnets:', error);
            alert('Error al cargar las subredes');
        });
}

function addSubnet(subnet) {
    fetch('/dashboard/settings/subnets', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ subnet: subnet })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addSubnetToList(subnet);
        } else {
            alert(data.message || 'Error al agregar la subred');
        }
    })
    .catch(error => {
        console.error('Error adding subnet:', error);
        alert('Error al agregar la subred');
    });
}

function deleteSubnet(subnet) {
    if (!confirm(`¿Está seguro que desea eliminar la subred ${subnet}?`)) {
        return;
    }
    
    fetch('/dashboard/settings/subnets', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ subnet: subnet })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.querySelector(`[data-subnet="${subnet}"]`).remove();
        } else {
            alert(data.message || 'Error al eliminar la subred');
        }
    })
    .catch(error => {
        console.error('Error deleting subnet:', error);
        alert('Error al eliminar la subred');
    });
}

function addSubnetToList(subnet) {
    const subnetList = document.getElementById('subnet-list');
    const item = document.createElement('div');
    item.className = 'subnet-item';
    item.setAttribute('data-subnet', subnet);
    
    item.innerHTML = `
        <span class="subnet-text">${subnet}</span>
        <button type="button" class="delete-subnet" onclick="deleteSubnet('${subnet}')">
            <i class="fas fa-trash"></i>
        </button>
    `;
    
    subnetList.appendChild(item);
} 