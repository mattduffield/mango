// https://github.com/samdutton/multi-input
// https://html.spec.whatwg.org/multipage/custom-elements.html#form-associated-custom-element
// https://html.spec.whatwg.org/multipage/custom-elements.html#custom-elements-face-example
// https://web.dev/more-capable-form-controls/

class MultiSelect extends HTMLElement {
	static formAssociated = true;
  
  constructor() {
    super();
    // Get access to the internal form control APIs
    this.internals_ = this.attachInternals();
    // internal value for this control
    this.value_ = 0;
    // This is a hack :^(.
    // ::slotted(input)::-webkit-calendar-picker-indicator doesn't work in any browser.
    // ::slotted() with ::after doesn't work in Safari.
    this.innerHTML += `
      <style>
        multi-select {
          display: flex;
          flex: 1 1 auto;
          min-height: 38px;
          border: 1px solid lightgray;
          border-radius: 5px;
          background-color: white;
        }      
        multi-select input::-webkit-calendar-picker-indicator {
          display: none;
        }
        /* NB use of pointer-events to only allow events from the × icon */
        multi-select div.item::after {
          color: black;
          content: '×';
          cursor: pointer;
          font-size: 18px;
          pointer-events: auto;
          position: absolute;
          right: 5px;
          top: -1px;
        }
      </style>`;
    this._shadowRoot = this.attachShadow({mode: 'open'});
    this._shadowRoot.innerHTML = `
      <style>
        :host {
          border: var(--multi-select-border, 1px solid #ddd);
          display: block;
          overflow: hidden;
          padding: 4px 8px;
        }
        /* NB use of pointer-events to only allow events from the × icon */
        ::slotted(div.item) {
          background-color: var(--multi-select-item-bg-color, #dedede);
          border: var(--multi-select-item-border, 1px solid #ccc);
          border-radius: 2px;
          color: #222;
          display: inline-block;
          font-size: var(--multi-select-item-font-size, 14px);
          margin: 2px;
          padding: 2px 25px 2px 5px;
          pointer-events: none;
          position: relative;
          top: -1px;
        }
        /* NB pointer-events: none above */
        ::slotted(div.item:hover) {
          background-color: #eee;
          color: black;
        }
        ::slotted(input) {
          border: none;
          font-size: var(--multi-select-input-font-size, 14px);
          outline: none;
          padding: 10px 10px 10px 5px;
          flex: 1 auto;
        }
      </style>
      <slot></slot>`;

    this._input = this.querySelector('input');
    this._input.onblur = this._handleBlur.bind(this);
    this._input.oninput = this._handleInput.bind(this);
    this._input.onkeydown = (event) => {
      this._handleKeydown(event);
    };

    this._allowDuplicates = this.hasAttribute('allow-duplicates');

    this._datalist = this.querySelector('datalist');
    this._allowedValues = [];
    this._selectedOptions = [];
    for (const option of this._datalist.options) {
    	if (option.dataset.selected) {
	      this._selectedOptions.push(option.value);    
      }
    }    
    for (const option of this._datalist.options) {
      this._allowedValues.push(option.value);
    }
  }

  // The following properties and methods aren't strictly required,
  // but browser-level form controls provide them. Providing them helps
  // ensure consistency with browser-provided controls.
  get form() { return this.internals_.form; }
  get name() { return this.getAttribute('name'); }
  get type() { return this.localName; }
  get validity() {return this.internals_.validity; }
  get validationMessage() {return this.internals_.validationMessage; }
  get willValidate() {return this.internals_.willValidate; }

  checkValidity() { return this.internals_.checkValidity(); }
  reportValidity() {return this.internals_.reportValidity(); }


	connectedCallback() {
    for (const option of this._selectedOptions) {
      this._addItem(option);
    }  
  }


  // Called by _handleKeydown() when the value of the input is an allowed value.
  _addItem(value) {
    this._input.value = '';
    const item = document.createElement('div');
    item.classList.add('item');
    item.textContent = value;
    this.insertBefore(item, this._input);
    item.onclick = () => {
      this._deleteItem(item);
    };

    // Remove value from datalist options and from _allowedValues array.
    // Value is added back if an item is deleted (see _deleteItem()).
    if (!this._allowDuplicates) {
      for (const option of this._datalist.options) {
        if (option.value === value) {
          option.remove();
        }
      }
      this._allowedValues =
      this._allowedValues.filter((item) => item !== value);
    }
    let values = this.getValues();
    this.internals_.setFormValue(values);
  }


  // Called when the × icon is tapped/clicked or
  // by _handleKeydown() when Backspace is entered.
  _deleteItem(item) {
    const value = item.textContent;
    item.remove();
    // If duplicates aren't allowed, value is removed (in _addItem())
    // as a datalist option and from the _allowedValues array.
    // So — need to add it back here.
    if (!this._allowDuplicates) {
      const option = document.createElement('option');
      option.value = value;
      // Insert as first option seems reasonable...
      this._datalist.insertBefore(option, this._datalist.firstChild);
      this._allowedValues.push(value);
    }
    let values = this.getValues();
    this.internals_.setFormValue(values);    
  }

  // Avoid stray text remaining in the input element that's not in a div.item.
  _handleBlur() {
    this._input.value = '';
  }

  // Called when input text changes,
  // either by entering text or selecting a datalist option.
  _handleInput() {
    // Add a div.item, but only if the current value
    // of the input is an allowed value
    const value = this._input.value;
    if (this._allowedValues.includes(value)) {
      this._addItem(value);
    }
  }

  // Called when text is entered or keys pressed in the input element.
  _handleKeydown(event) {
    const itemToDelete = event.target.previousElementSibling;
    const value = this._input.value;
    // On Backspace, delete the div.item to the left of the input
    if (value ==='' && event.key === 'Backspace' && itemToDelete) {
      this._deleteItem(itemToDelete);
    // Add a div.item, but only if the current value
    // of the input is an allowed value
    } else if (this._allowedValues.includes(value)) {
      this._addItem(value);
    }
  }

  // Public method for getting item values as an array.
  getValues() {
    const values = [];
    const items = this.querySelectorAll('.item');
    for (const item of items) {
      values.push(item.textContent);
    }
    return values;
  }
}

window.customElements.define('multi-select', MultiSelect);
