

label_class = 'block text-gray-700 text-sm font-light mb-2'
input_class = '''
  form-control
  block
  w-full
  px-3
  py-1.5
  text-base
  font-normal
  text-gray-700
  bg-white bg-clip-padding
  border border-solid border-gray-300
  rounded
  transition
  ease-in-out
  m-0
  focus:text-gray-700 focus:bg-white focus:outline-none
  ring-primary
'''
textarea_class = '''
  form-control
  block
  w-full
  px-3
  py-1.5
  text-base
  font-normal
  text-gray-700
  bg-white bg-clip-padding
  border border-solid border-gray-300
  rounded
  transition
  ease-in-out
  m-0
  h-48
  focus:text-gray-700 focus:bg-white focus:outline-none
  ring-primary
'''
textarea_small_class = '''
  form-control
  block
  w-full
  px-3
  py-1.5
  text-base
  font-normal
  text-gray-700
  bg-white bg-clip-padding
  border border-solid border-gray-300
  rounded
  transition
  ease-in-out
  m-0
  h-24
  focus:text-gray-700 focus:bg-white focus:outline-none
  ring-primary
'''
chk_class = '''
  form-check-input
  xappearance-none
  h-4
  w-4
  border
  border-gray-300
  rounded-sm
  bg-white
  checked:bg-blue-600
  checked:border-blue-600
  focus:outline-none
  transition
  duration-200
  mt-1
  align-top
  bg-no-repeat
  bg-center
  bg-contain
  float-left
  mr-2
  cursor-pointer
  ring-primary
'''
select_class = '''form-select appearance-none
  block
  w-full
  px-3
  py-1.5
  text-base
  font-normal
  text-gray-700
  bg-white bg-clip-padding bg-no-repeat
  border border-solid border-gray-300
  rounded
  transition
  ease-in-out
  m-0
  focus:text-gray-700 focus:bg-white focus:outline-none
  ring-primary
'''
select_multiple_class = '''
  xblock
  xw-full
  xtext-base
  xfont-normal
  xtext-gray-700
  xbg-white bg-clip-padding
  xborder border-solid border-transparent
  xrounded
  xtransition
  xease-in-out
  xm-0
'''
toggle_radio_class = '''
  w-full
  transition
  ease-in-out
  focus:text-gray-700 focus:bg-white focus:outline-none
  toggle-radio
  ring-primary
'''
toggle_switch_class = '''
  toggle-switch-container
  cursor-pointer
  ring-primary
'''

hs_element_type_true_targets = ["inner_text", "inner_html"]
hs_element_type_false_targets = ["field", "label_class", "label_class_use_quotes"]
hs_element_type = f'''
on change
  toggleTableRowHidden(me, "element_type", {hs_element_type_true_targets}, {hs_element_type_false_targets}, "element")
end
on load
  toggleTableRowHidden(me, "element_type", {hs_element_type_true_targets}, {hs_element_type_false_targets}, "element")
end
'''

hs_data_type = f'''
on load
  if me.value == 'bool'
    filterSelectOptionsByValues(me, "#field_type", ["BooleanField", "ToggleSwitchField"])
  end
  if me.value == 'datetime'
    filterSelectOptionsByValues(me, "#field_type", ["DateField"])
  end
  if me.value == 'Dict'
    filterSelectOptionsByValues(me, "#field_type", ["FormField"])
  end
  if me.value == 'int'
    filterSelectOptionsByValues(me, "#field_type", ["IntegerField"])
  end
  if me.value == 'List'
    filterSelectOptionsByValues(me, "#field_type", ["FieldList", "QuerySelectMultipleField"])
  end
  if me.value == 'PositiveInt'
    filterSelectOptionsByValues(me, "#field_type", ["IntegerField"])
  end
  if me.value == 'str'
    filterSelectOptionsByValues(me, "#field_type", ["CodeMirrorField", "ColorField", "CurrencyField", "DatalistField", "EmailField", "LookupSelectField", "PicklistSelectField", "QuerySelectField", "StringField", "TextAreaField"])
  end
on change 
  if me.value == 'bool'
    filterSelectOptionsByValues(me, "#field_type", ["BooleanField", "ToggleSwitchField"])
  end
  if me.value == 'datetime'
    filterSelectOptionsByValues(me, "#field_type", ["DateField"])
  end
  if me.value == 'Dict'
    filterSelectOptionsByValues(me, "#field_type", ["FormField"])
  end
  if me.value == 'int'
    filterSelectOptionsByValues(me, "#field_type", ["IntegerField"])
  end
  if me.value == 'List'
    filterSelectOptionsByValues(me, "#field_type", ["FieldList", "QuerySelectMultipleField"])
  end
  if me.value == 'PositiveInt'
    filterSelectOptionsByValues(me, "#field_type", ["IntegerField"])
  end
  if me.value == 'str'
    filterSelectOptionsByValues(me, "#field_type", ["CodeMirrorField", "ColorField", "CurrencyField", "DatalistField", "EmailField", "LookupSelectField", "PicklistSelectField", "QuerySelectField", "StringField", "TextAreaField"])
  end
'''

hs_field_type = f'''
on load
  if not (the closest <div.wrapper.hidden/>)
    toggleElementVisibility(me, "query-tab-container", ["LookupSelectField", "QuerySelectField", "QuerySelectMultipleField"])
    toggleElementVisibility(me, "allow-blank-container", ["LookupSelectField", "PicklistSelectField", "QuerySelectField"])
    toggleElementVisibility(me, "wrapper_field_type_form_field", ["FieldList", "FormField"])
    toggleElementVisibility(me, "wrapper_datalist", ["DatalistField", "PicklistSelectField"])
    toggleElementVisibility(me, "wrapper_placeholder", ["StringField"])
  end
on change 
  toggleElementVisibility(me, "query-tab-container", ["LookupSelectField", "QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "allow-blank-container", ["LookupSelectField", "PicklistSelectField", "QuerySelectField"])
  toggleElementVisibility(me, "wrapper_field_type_form_field", ["FieldList", "FormField"])
  toggleElementVisibility(me, "wrapper_datalist", ["DatalistField", "PicklistSelectField"])
  toggleElementVisibility(me, "wrapper_placeholder", ["StringField"])
'''

hs_field_type_form_field = f'''
on load
  if not (the closest <div.wrapper.hidden/>)
    toggleElementVisibility(me, "wrapper_datalist", ["DatalistField"])
  end
on change 
  toggleElementVisibility(me, "wrapper_datalist", ["DatalistField"])
'''


hs_field_type2 = f'''
on load 
  toggleElementVisibility(me, "wrapper_collection", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_projection_list", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_query_list", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_order_by_list", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_display_member", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_value_member", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_allow_blank", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_blank_text", ["QuerySelectField", "QuerySelectMultipleField"])
end
on change 
  toggleElementVisibility(me, "wrapper_collection", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_projection_list", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_query_list", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_order_by_list", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_display_member", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_value_member", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_allow_blank", ["QuerySelectField", "QuerySelectMultipleField"])
  toggleElementVisibility(me, "wrapper_blank_text", ["QuerySelectField", "QuerySelectMultipleField"])
end
'''

hs_config_tom_select = f'''
on load 
  configTomSelect(me)
'''

hs_config_rome = f'''
on load 
  configRome(me)
'''
