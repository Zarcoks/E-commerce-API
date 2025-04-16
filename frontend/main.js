const API_BASE = 'http://localhost:5000';
let currentOrderId = null;
let cart = [];
let allProducts = [];

function showError(msg) {
  const errBox = document.getElementById('error');
  errBox.textContent = msg;
  errBox.classList.remove('hidden');
}

function hideError() {
  document.getElementById('error').classList.add('hidden');
}

async function fetchProducts() {
  const res = await fetch(`${API_BASE}/`);
  const products = await res.json();
  allProducts = products; 
  const bar = document.getElementById('products-bar');
  products.forEach(p => {
    const el = document.createElement('div');
    el.className = 'product';
    el.innerHTML = `<strong>${p.name}</strong><br>${p.description}<br>${p.price} $<br><button onclick="addToCart(${p.id})">Ajouter</button>`;
    bar.appendChild(el);
  });
}

function addToCart(id, name) {
  const existing = cart.find(p => p.id === id);
  if (!existing) {
    cart.push({ id, quantity: 1, name: name });
  }
  updateCartDisplay();
}

function updateCartDisplay() {
  const container = document.getElementById('cart-items');
  container.innerHTML = '';
  cart.forEach((item, idx) => {
    const product = allProducts.find(p => p.id === item.id);
    const div = document.createElement('div');
    div.innerHTML = `${product ? product.name : 'Produit inconnu'} - Quantité : 
      <select onchange="updateQty(${idx}, this.value)">
        ${[1,2,3,4,5].map(v => `<option ${v==item.quantity?'selected':''}>${v}</option>`).join('')}
      </select>`;
    container.appendChild(div);
  });
}

function updateQty(index, value) {
  cart[index].quantity = parseInt(value);
}

document.getElementById('create-order-form').addEventListener('submit', async e => {
  e.preventDefault();
  hideError();
  const res = await fetch(`${API_BASE}/order`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ products: cart })
  });
  if (!res.ok) return showError('Erreur lors de la création.');
  const data = await res.json();
  currentOrderId = data.id;
  document.getElementById('order-update').classList.remove('hidden');
});

document.getElementById('update-order-form').addEventListener('submit', async e => {
  e.preventDefault();
  hideError();
  const f = e.target;
  const body = {
    order: {
      email: f.email.value,
      shipping_information: {
        country: f.country.value,
        address: f.address.value,
        postal_code: f.postal_code.value,
        city: f.city.value,
        province: f.province.value
      }
    }
  };
  const res = await fetch(`${API_BASE}/order/${currentOrderId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) return showError('Erreur lors de la mise à jour.');
  document.getElementById('credit-card').classList.remove('hidden');
});

document.getElementById('credit-card-form').addEventListener('submit', async e => {
  e.preventDefault();
  hideError();
  const f = e.target;
  const body = {
    credit_card: {
      name: f.name.value,
      number: f.number.value,
      expiration_year: parseInt(f.expiration_year.value),
      expiration_month: parseInt(f.expiration_month.value),
      cvv: f.cvv.value
    }
  };
  const res = await fetch(`${API_BASE}/order/${currentOrderId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) return showError('Erreur de paiement.');
  alert('Paiement réussi !');
});

document.getElementById('get-order-form').addEventListener('submit', async e => {
  e.preventDefault();
  hideError();
  const id = e.target.order_id.value;
  const res = await fetch(`${API_BASE}/order/${id}`);
  const data = await res.json();
  document.getElementById('order-response').textContent = JSON.stringify(data, null, 2);
});

fetchProducts();