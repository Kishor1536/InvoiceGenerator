import streamlit as st
import pandas as pd
from weasyprint import HTML
from datetime import datetime
import io

# Load HTML template
def load_template():
    with open('invoice_template.html', 'r', encoding='utf-8') as f:
        return f.read()

# Populate template with data
def populate_template(html, data, items_df):
    # Replace placeholders
    for key, val in data.items():
        html = html.replace(f'{{{{{key}}}}}', str(val))
    
    # Calculate totals
    subtotal = items_df['total'].sum()
    tax = subtotal * 0.18
    grand_total = subtotal + tax
    
    # Replace total placeholders (matching the template exactly)
    html = html.replace('{{subtotal}}', f'₹{subtotal:,.2f}')
    html = html.replace('{{tax}}', f'₹{tax:,.2f}')
    html = html.replace('{{grand_total}}', f'₹{grand_total:,.2f}')
    
    # Generate item rows with tax per item
    rows = ""
    for idx, row in items_df.iterrows():
        item_tax = row['total'] * 0.18
        item_with_tax = row['total'] + item_tax
        rows += f"""
            <tr>
                <td>{idx + 1}</td>
                <td>{row['description']}</td>
                <td class="text-right">{int(row['qty'])}</td>
                <td class="text-right">₹{row['unit_price']:,.2f}</td>
                <td class="text-right">₹{row['total']:,.2f}</td>
                <td class="text-right">₹{item_tax:,.2f}</td>
                <td class="text-right">₹{item_with_tax:,.2f}</td>
            </tr>"""
    
    return html.replace('{{items}}', rows)

# Convert HTML to PDF
def html_to_pdf(html):
    buffer = io.BytesIO()
    HTML(string=html).write_pdf(buffer)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.set_page_config(page_title="Invoice Generator", page_icon="📄", layout="wide")
st.title("📄 Invoice Generator")

# Initialize items
if 'items' not in st.session_state:
    st.session_state['items'] = [
        {'description': 'Service 1', 'qty': 1, 'unit_price': 1000.00},
        {'description': 'Service 2', 'qty': 2, 'unit_price': 2000.00},
    ]

# Sidebar - Invoice Details
with st.sidebar:
    st.header("Invoice Details")
    invoice_number = st.text_input("Invoice #", "INV-001")
    invoice_date = st.date_input("Date", datetime.now())
    due_date = st.date_input("Due Date")
    
    st.header("Company")
    company_name = st.text_input("Name", "Your Company")
    company_address = st.text_area("Address", "123 Business St\nCity, State 12345")
    
    st.header("Bill To")
    bill_to_name = st.text_input("Client Name", "Client Company")
    bill_to_address = st.text_area("Client Address", "456 Client Ave\nCity, State 67890")

# Main area - Items
st.subheader("Invoice Items")

# Display items
for i, item in enumerate(st.session_state['items']):
    cols = st.columns([4, 1, 1.5, 1.5, 0.5])
    item['description'] = cols[0].text_input("Description", item['description'], key=f"d{i}", label_visibility="collapsed")
    item['qty'] = cols[1].number_input("Qty", value=item['qty'], min_value=1, key=f"q{i}", label_visibility="collapsed")
    item['unit_price'] = cols[2].number_input("Price", value=item['unit_price'], min_value=0.01, key=f"p{i}", label_visibility="collapsed")
    item['total'] = item['qty'] * item['unit_price']
    cols[3].markdown(f"**₹{item['total']:,.2f}**")
    if cols[4].button("🗑️", key=f"del{i}"):
        st.session_state['items'].pop(i)
        st.rerun()

# Add item button
if st.button("➕ Add Item"):
    st.session_state['items'].append({'description': 'New Item', 'qty': 1, 'unit_price': 100.00})
    st.rerun()

# Calculate summary
items_df = pd.DataFrame(st.session_state['items'])
subtotal = items_df['total'].sum()
tax = subtotal * 0.18
grand_total = subtotal + tax

# Display summary
st.markdown("---")
col1, col2 = st.columns([2, 1])
with col2:
    st.markdown(f"**Subtotal:** ₹{subtotal:,.2f}")
    st.markdown(f"**Tax (18%):** ₹{tax:,.2f}")
    st.markdown(f"### **Total: ₹{grand_total:,.2f}**")

# Generate PDF button
st.markdown("---")
if st.button("🎨 Generate Invoice PDF", type="primary", use_container_width=True):
    data = {
        'company_name': company_name,
        'company_address': company_address.replace('\n', '<br>'),
        'invoice_number': invoice_number,
        'invoice_date': invoice_date.strftime('%d-%m-%Y'),
        'due_date': due_date.strftime('%d-%m-%Y'),
        'bill_to_name': bill_to_name,
        'bill_to_address': bill_to_address.replace('\n', '<br>')
    }
    
    html = populate_template(load_template(), data, items_df)
    pdf = html_to_pdf(html)
    
    st.success("✅ Invoice Generated!")
    st.download_button("📥 Download PDF", pdf, f"invoice_{invoice_number}.pdf", "application/pdf", use_container_width=True)
