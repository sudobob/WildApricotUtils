$(document).ready(() => {
/* 
 * wautils.js
 *
 * implements browser-side functionality for the novalabs wild apricot utilities
 *
 * works with the wautils.nova-labs.org python flask web appliction
 *
 */

$(document).ready(() => {

function filt_signoff(substr) {
  // on keyup in the search box we display only the signoffs that match
  $('.signoff_item_div').filter(function() {
    // console.log(substr);
    $(this).toggle($(this).text().toUpperCase().indexOf(substr) > -1)
  });
}

function filt_member(substr) {
  // on keyup from the member search we show only members that match
  $('.contacts_tr').filter(function() {
    $(this).toggle($(this).text().toUpperCase().indexOf(substr) > -1)
  });
}

//
// event listeners for form elements
//
$(document).on('click', '#member_show_all_tog_but', () => {
  console.log('member_show_all_tog_but');
  $('.contacts_tr').show('fast');
});
$(document).on('keyup', '#member_search_inp', function() { // doesn't work:() => {
  filt_member( $(this).val().toUpperCase() );
});
$(document).on('keyup', '#signoff_edit_search_inp', function() { // doesn't work: () => {
  filt_signoff( $(this).val().toUpperCase() );
});
$(document).on('click', '#signoff_edit_show_all_tog_but', () => {
    $('.signoff_item_div').show('fast');
});
$(document).on('click','#signoff_edit_check_all_but', () => {
  $('.signoff_item_div:not(:hidden) > input').attr('checked',true);
});

$(document).on('click','#signoff_edit_save_but', () => {
  signoffs_save(); 
});

$(document).on('click','#signoff_edit_uncheck_all_but', () => {
  $('.signoff_item_div:not(:hidden) > input').attr('checked',false);
});

$(document).on('click', '#render_contacts_but', () => {
  hide_maindiv().then( ()=>{ process_contacts(window.wautils_contacts); show_maindiv(); });
});
$(document).on('click', '.signoff_edit_but', function()  {
  // <button class="btn btn-primary btn-inline btn-sm m-1 signoff_edit_but" id="show_wc_">WC_</button>
  //                                                                 look for this:  ^^^
  filt_signoff( $(this).attr('id').replace('show_','').toUpperCase());
});

$(document).on('click', '#signoff_edit_show_checked_but', () => {
  // hide all unchecked
  $('.signoff_item_div').find('input:checkbox:not(:checked)').parent().hide();
  // show checked
  $('.signoff_item_div').find('input:checked').parent().show();
});

$(document).on('click', '.contact_row_edit',function()  {
  // they've clicked the edit icon on one contact
  // go edit it
  hide_maindiv().then( ()=>{
    contact_index = $(this).attr('id').replace('ci_',''); // retrieve contact index from div id= 
    contact_id  = window.wautils_contacts[0].Contacts[contact_index]['Id']; // save just the wa contact Id
    window.wautils_contact_index_list.push(contact_index);
    contact_to_edit = window.wautils_contacts[0].Contacts[contact_index]; // retreive just this contact object
    signoffs_edit_render(contact_to_edit);  // go edit it
    show_maindiv();
  });
});

$(document).on('click', '.member_row_edit',function()  {
  // they've clicked the edit icon on one contact
  // go edit it
  hide_maindiv().then( ()=>{
    contact_index = $(this).attr('id').replace('ci_',''); // retrieve contact index from div id= 
    contact_id  = window.wautils_contacts[0].Contacts[contact_index]['Id']; // save just the wa contact Id
    window.wautils_contact_index_list.push(contact_index);
    contact_to_edit = window.wautils_contacts[0].Contacts[contact_index]; // retreive just this contact object
    member_edit_render(contact_to_edit);  // go edit it
    show_maindiv();
  });
});

$(document).on('click', '.event_row_edit_btn',function()  {
  console.log('event_row_edit_btn click');

  hide_maindiv()
    .then(show_loader)
    .then(get_event_registrations($(this).attr('id')))
    .then(hide_loader)
    .then(show_maindiv)





});


/*
attempt to log us out of wa doesn't work yet
$(document).on('click', '#nav_logout',function()  {
  $.ajax({
    type: 'GET',
    url  : 'https://portal.nova-labs.org/Sys/Login/Signout',
    headers: {  'Access-Control-Allow-Origin': '*' },
    failure: (errMsg) => { alert("FAIL:" + errMsg); },
    error: (xh,ts,et) =>  { alert("FAIL:" + u + ' ' + et); },
    contentType: false,
    processData: false
  });

});
*/

function extract_contentfield(j,fieldname) {
  // called from the get 
  // consume output of /accounts/{accountId}/contactfields

  console.log("extract_contentfield()");


  var signoff_fields = [];

  // save it away for later
  window.wautils_contact_fields = j; 
  $.each(j,(k,v) => {
    // find NL Signoffs and Categories then extract
    // all possible AllowedValues
    if (v['FieldName'] !== fieldname) 
      return true

    $.each(v['AllowedValues'],(kk,vv) => {
      /* o += '<pre>' + vv['Label'] + '</pre>'; */
      signoff_fields.push(
        {
          'Label': vv['Label'],
          'Id': vv['Id']
        }
      );
    });


    /*
     signoff_fields:
      [
        {
          "Label": "[equipment] *GREEN",
          "Id": 11968550
        },
        ...
        {
          "Label": "[novapass] WWR_SawStop_Table Saw",
          "Id": 11968626
        }
      ] 
      */
      window.wautil_signoff_fields = signoff_fields;


  });
}


function process_contacts(j) {
  mode = document.getElementsByTagName("title")[0].innerHTML;


  
  if (j['error'] == 1) {
    m(j['error_message'],'warning');
  } else  {
    //
    // render pick member page
    //
    o = '';
    o += '<p class="bigger">Pick Member</p>';
    o += '<div class="form-group form-inline">';
    o += '<input class="input" id="member_search_inp" type="text" placeholder="Filter..">';
    o += '<button class="btn btn-primary btn-inline btn-sm" id="member_show_all_tog_but">ALL</button>';
    o += '</div>';
    o += '<table class="table table-striped"><thead><tr>';
    o += '<th></th>';
    o += '<th>First Name</th>';
    o += '<th>Last Name</th>';
    o += '<th>Email</th>';

    if (mode == 'signoffs') {
      o += '<th>Signoffs</th>';
    } else if (mode == 'members') {
      o += '<th>Membership</th>';
    }
    o += '</tr></thead>';

    $.each(j[0].Contacts,(k,v) => {
      // each row will be a member
      //console.log(v['Email']);
      //if (v['Email'] !== 're_wa_associate_test_1@cogwheel.com') 
      //  return true;
      //
      if (v['Email'] == '' ||
        v['FirstName'] == '' ||
        v['LastName'] == '' ) 
        return true; // skip empties

      is_a_member = true; // https://www.youtube.com/watch?v=F7T7fOXxMEk


      o += '<tr class="contacts_tr">'

      o += '<td>'
      if (mode == 'signoffs') {
      contact_index = 'ci_' + k;
      o += ` 
        <button 
           class="btn btn-sm contact_row_edit btn-primary" 
           id="${contact_index}"
           data-toggle="tooltip" 
           data-placement="right" 
           title="edit signoffs"> 
        <i class="far fa-edit"></i> </button>
`
      } else if (mode == 'members') {

      contact_index = 'ci_' + k;
      o += ` 
        <button 
           class="btn btn-sm member_row_edit btn-primary" 
           id="${contact_index}"
           data-toggle="tooltip" 
           data-placement="right" 
           title="edit member"> 
        <i class="far fa-edit"></i> </button>
`
      }
      o += '</td>'

      o += '<td>'
      o += v['FirstName'];
      o += '</td>'

      o += '<td>'
      o += v['LastName'];
      o += '</td>'

      o += '<td>'
      o += v['Email'];
      o += '</td>'

      //console.log(JSON.stringify(v,null,'\t'));
    
      if (mode == 'signoffs') {
      o += '<td>'

        // in the case of signoffs we show the signoffs

        o += '<table class="table table-striped"><thead><tr>';

        $.each(v['FieldValues'],(kk,vv) => {
          // go fish for the right FieldValue 
          if (vv['FieldName'] != 'NL Signoffs and Categories') 
            return true; // we are just looking for the NL Signoffs and Categories field
          // 45: {FieldName: "NL Signoffs and Categories", Value: Array(4), SystemCode: "custom-11058873"}
          //                 save this for when we POST our updated info        ^^^^^^^^^^^^^^^
          window.wautils_equipment_signoff_systemcode = vv['SystemCode'];
          o += '<td>'
          $.each(vv['Value'],(kkk,vvv) => {
            o += vvv['Label'];
            o += '<br>';
          });
          o += '</td>'
          o += '</tr>'
        });
      o += '</table>';
      o += '</td>'
      } else if (mode == 'members') {

        // if displaying for member editing we show member level
        $.each(v['FieldValues'],(kk,vv) => {
          if (vv['FieldName'] != 'Membership level ID') 
            return;

          o += '<td>';
          // the contacts record gives us just the level ID
          level_id = vv.Value;
          $.each( window.wautils_membershiplevels, (kkk,vvv) => {
            // so then we look it up in the wautils_membershiplevels
            if (level_id == vvv.Id) {
              o += vvv.Name; 
            }
          });
          o += '</td>';
        });

      }
      /*
      if (mode == 'members') {
        o += '<table class="table table-striped"><thead><tr>';
        o += '<td>'
        o += '<pre>'
        o += JSON.stringify(v,null,'\t');
        o += '</pre>'
        o += '</td>'
        o += '</tr>'
        o += '</table>';

      }
*/



      o += '</tr>'
    });
    o += '</table>';
    $('#maindiv').html(o);
  }
}


function m(mesg,color) {
  // Put up a message on the UI.
  // append message unless mesg is ''
  o = '<div class="alert alert-' + color + '" role="alert">'
  o += mesg;
  o += '</div>'
  if (mesg == '')
    $('#topdiv').html(o);
  else 
    $('#topdiv').append(o);
}

function get_membershiplevels() {
  return new Promise (function(resolve,reject) {
    // get list of possible signoffs
    // https://app.swaggerhub.com/apis-docs/WildApricot/wild-apricot_public_api/2.1.0#/Contacts.CustomFields/GetContactFieldDefinitions
    $.ajax({
      type: 'GET',
      url  : '/api/v1/wa_get_any_endpoint',
      // string '$accountid' will get replaced with real account id on server
      data : $.param({'endpoint':'accounts/$accountid/membershiplevels'}),
      success: (j) => { 
          window.wautils_membershiplevels = j; // save for later
          resolve();
      }, 
      failure: (errMsg) => { alert("FAIL:" + errMsg); },
      error: (xh,ts,et) =>  { alert("FAIL:" + u + ' ' + et); },
      contentType: false,
      processData: false
    });


  });
}
function get_signoffs() {
  return new Promise (function(resolve,reject) {
    // get list of possible signoffs
    // https://app.swaggerhub.com/apis-docs/WildApricot/wild-apricot_public_api/2.1.0#/Contacts.CustomFields/GetContactFieldDefinitions
    console.log("get_signoffs()");
    $.ajax({
      type: 'GET',
      url  : '/api/v1/wa_get_any_endpoint',
      // string '$accountid' will get replaced with real account id on server
      data : $.param({'endpoint':'/accounts/$accountid/contactfields'}),
      success: (j) => { 
        extract_contentfield(j,'NL Signoffs and Categories');resolve(); 
      }, 
      failure: (errMsg) => { alert("FAIL:" + errMsg); },
      error: (xh,ts,et) =>  { alert("FAIL:" + u + ' ' + et); },
      contentType: false,
      processData: false
    });


  });
}

function get_contacts() {
  // get contacts list
  // https://app.swaggerhub.com/apis-docs/WildApricot/wild-apricot_public_api/2.1.0#/Contacts/GetContactsList
  return new Promise(function(resolve,reject) {
    u  = '/api/v1/wa_get_any_endpoint',
      $.ajax({
        type: 'GET',
        url  : u,
        // string '$accountid' will get replaced with real account id on server
        data : $.param({'endpoint':'accounts/$accountid/contacts/?$async=false'}),
        success: (j) => { 
          window.wautils_contacts = j; // save for later
          process_contacts(window.wautils_contacts);
          resolve();  
        }, 
        failure: (errMsg) => { alert("FAIL:" + errMsg); },
        error: (xh,ts,et) =>  { alert("FAIL:" + u + ' ' + et); },
        contentType: false,
        processData: false
      });

  });
}


function show_loader() {
  return new Promise( function(resolve,reject) {
    $('#loaderdiv').show('fast',resolve);
  });
}
function hide_loader() {
  return new Promise( function(resolve,reject) {
    $('#loaderdiv').hide('fast',resolve);
  });
}
function show_maindiv() {
  return new Promise( function(resolve,reject) {
    $('#maindiv').show('fast',resolve);
  });
}
function hide_maindiv() {
  return new Promise( function(resolve,reject) {
    $('#maindiv').hide('fast',resolve);
  });
}

function signoff_edit_emit_row(lhs,rhs) {
  // generate one row of the signoff page
  o = '';

  o += '<tr>';
  o += '  <td style="width:20%;text-align:right;"><b>' + lhs + '</b></td>';
  o += '  <td style="width:80%;text-align:left;">' + rhs + '</td>';
  o += '</tr>';
  return o;

}
function get_contacts_signed_off_items(contact_to_edit) {
  // return contact's signed-off items:
  existing_signoffs = [];
  $.each(contact_to_edit['FieldValues'],(kk,vv) => {
    if (vv['FieldName'] != 'NL Signoffs and Categories') 
      return true
    existing_signoffs = vv;
    return false;
  });

  so_items = [];
  $.each(existing_signoffs['Value'],(kk,vv) => {
    so_items.push(
      {
        'Label': vv['Label'],
        'Id': vv['Id']
      }
    )
  });
  /* so_items:
  0: {Label: "[equipment] *GREEN", Id: 11968550}
  1: {Label: "[novapass] CC_ShopSabre_CNC Router", Id: 11968621}
  2: {Label: "[novapass] LC_Hurricane_Laser Cutter", Id: 11968622}
  3: {Label: "[novapass] LC_Rabbit_Laser Cutter", Id: 11968623}
  */
  return so_items;
};

function has_signoff(contact_id,signoff_name) {
  // does contact_id have signoff_name ? 
  $.each(contact_to_edit['FieldValues'],(kk,vv) => {
    if (vv['FieldName'] != 'NL Signoffs and Categories') 
      return true
    exisiting_signoffs = vv;
    return false;
  });

  /*
  {
  FieldName: "NL Signoffs and Categories"
  SystemCode: "custom-11058873"
  Value: Array(4)
  0: {Id: 11968550, Label: "[equipment] *GREEN"}
  1: {Id: 11968621, Label: "[novapass] CC_ShopSabre_CNC Router"}
  2: {Id: 11968622, Label: "[novapass] LC_Hurricane_Laser Cutter"}
  3: {Id: 11968623, Label: "[novapass] LC_Rabbit_Laser Cutter"}
  */
  var has_signoff = false;
  $.each(exisiting_signoffs['Value'],(kk,vv) => {
    if (vv['Label'] != signoff_name)
      return true
    has_signoff = true
    return false;
  });

}

function signoff_edit_emit_signoffs(contact_to_edit) {
  // List all possible sign-offs. 
  // Check items which user has been checked off on 
  var o = '';
  o += '<form class="form">';
  contacts_signed_off_items = get_contacts_signed_off_items(contact_to_edit);
  $.each(window.wautil_signoff_fields,(k,v) => {
    // iterate  through the list of all possible signoffs
    checked = '';
    if (contacts_signed_off_items.find(x => x.Id == v['Id']))
      // if current contact's has signoffs, mark then checked 
      checked = 'checked';

    // emit html
    o += signoff_emit_signoff_item(contact_to_edit['Id'],v['Id'],v['Label'],checked);
  });

  o += '</form>';
  return o;

}

function signoff_emit_signoff_item(cid,fid,label,checked) {
  // output html for single checkoff
  // cid  : contact id
  // fid : field id
  // label : text to display
  // checked : if we should mark it checked

  var o = '';

  o += '  <div id="cid_'+cid+'" class="form-check signoff_item_div">';
  o += '    <input type="checkbox" class="form-check-input" id="fid_' + fid + '" ' + checked + ' >';
  o += '    <label class="form-check-label" for="fid_' + fid + '">' + label + '</label>';
  o += '  </div>';

  return o;

}

function signoffs_edit_render(contact_to_edit) {

  // display single contact's editable signoffs

  o = '';

  // show name email of member
  o += '<p class="bigger"><b>' + 
    contact_to_edit['FirstName'] + ' ' + contact_to_edit['LastName'] +
    ' (' + contact_to_edit['Email'] + ') </b></p>';

  // search box and buttons
  o += '<hr>';
  o += '<div class="form-group form-inline m-0">';
  o += '<p><b>SHOW:&nbsp;</b></p>';
  o += '   <input class="input" id="signoff_edit_search_inp" type="text" placeholder="Search..">';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1" id="signoff_edit_show_all_tog_but">ALL POSSIBLE</button>';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1" id="signoff_edit_show_checked_but">ALREADY CHECKED</button>';
  o += '</div>';
  o += '<div class="form-group form-inline m-0">';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1 signoff_edit_but" id="show_go_"><b>GO</b></button>';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1 signoff_edit_but" id="show_lc_">LASER</button>';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1 signoff_edit_but" id="show_ac_">ARTS&CRAFTS</button>';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1 signoff_edit_but" id="show_bl_">BLACKSMITH</button>';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1 signoff_edit_but" id="show_cc_">CNC</button>';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1 signoff_edit_but" id="show_el_">ELECTRONICS</button>';
  o += '</div>';
  o += '<div class="form-group form-inline m-0">';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1 signoff_edit_but" id="show_mw">METALSHOP</button>';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1 signoff_edit_but" id="show_mwy_">METALSHOP YELLOW</button>';
  o += '</div>';
  o += '<div class="form-group form-inline m-0">';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1 signoff_edit_but" id="show_ww">WOODSHOP</button>';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1 signoff_edit_but" id="show_wwl_">WOODSHOP LATHE</button>';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1 signoff_edit_but" id="show_wwy_">WOODSHOP YELLOW</button>';
  o += '   <button class="btn btn-warning btn-inline btn-sm m-1 signoff_edit_but" id="show_wwr_">WOODSHOP RED</button>';
  o += '</div>';
  o += '<hr>';
  o += '<div class="form-group form-inline m-0">';
  o += '<p><b>ACTIONS:</b></p>';
  o += '   <button class="btn btn-primary btn-inline btn-sm m-1" id="signoff_edit_check_all_but">CHECK ALL SHOWN</button>';
  o += '   <button class="btn btn-primary btn-inline btn-sm m-1" id="signoff_edit_uncheck_all_but">UNCHECK ALL SHOWN</button>';
  o += '   <button class="btn btn-primary btn-inline btn-sm m-1" id="render_contacts_but">BACK TO PICK MEMBER</button>';
  o += '   <button class="btn  btn-inline btn-sm m-1 btn-success" id="signoff_edit_save_but">SAVE</button>';
  o += '</div>';

  o += '<hr>';

  o += '<div>';
  o += signoff_edit_emit_signoffs(contact_to_edit); 

  $('#maindiv').html(o);

}

function emit_member_row(lhs,rhs) {

  o = '<!-- -->';
  o += '<div class="row">';
  o += '<div class="col-2"><p style="text-align:right;margin:4px;font-weight:600">' + lhs + '</p></div>';
  o += '<div class="col-6"><p style="text-align:left;margin:4px;">' + rhs + '</p></div>';
  o += '</div>';
  o += '<!-- -->';
  return o;

}


function member_edit_render(ct) {

  // display single contact's editable signoffs

  o = '';

  // search box and buttons

  o += emit_member_row('FirstName',ct['FirstName']);
  o += emit_member_row('LastName',ct['LastName']);
  o += emit_member_row('Email',ct['Email']);
  o += emit_member_row('MembershipLevel',ct['MembershipLevel'].Name);


  $.each(ct['FieldValues'],(k,v) => {
    if (v.FieldName  == "Primary Member ID")
      o += emit_member_row(v.FieldName,v.Value);
  });

  
  oo = ''
  oo = '<select name="pkm" id="pkm">'
  pkm =  get_key_prime_key_members() 

  $.each(pkm,(k,v) => {
    oo += '<option value="' + v.name + '">' + v.name + '</option>'
  });

  oo += '</select>'

  o += emit_member_row('Pick Primary Member',oo);

  /*


  o += '   <button class="btn btn-primary btn-inline btn-sm m-1" id="render_contacts_but">BACK TO PICK MEMBER</button>';
  o += '   <button class="btn  btn-inline btn-sm m-1 btn-success" id="member_edit_save_but">SAVE</button>';
  // https://bootstrap-table.com/docs/getting-started/usage/#via-javascript


  */
  o += '<table class="table table-striped"><thead><tr>';
  o += '<td>'
  o += '<pre>'
  o += JSON.stringify(contact_to_edit,null,'\t');
  o += '</pre>'
  o += '</td>'
  o += '</tr>'
  o += '</table>';

  $('#maindiv').html(o);

}
function get_key_prime_key_members() {

  pkm = []
  $.each(window.wautils_contacts[0].Contacts,(k,v) => {
    if (('MembershipLevel' in v)) {
    if ( v['MembershipLevel'].Name.includes('Key') && 
        !v['MembershipLevel'].Name.includes('amily'))
        pkm.push({'name':v.DisplayName,
                          'email':v.Email,
                          'id':v.Id
                        })

    }
  });
  return pkm
}

function signoffs_save() {
  //
  // update member's signoffs in WA and locally
  //
  checked_divs = $('.signoff_item_div > input:checked').parent();

  if (wautils_contact_index_list.length)
    contact_index = wautils_contact_index_list.pop(); 

  this_contact = window.wautils_contacts[0].Contacts[contact_index]
  this_contact_id = this_contact['Id'];
  signoff_idx = window.wautils_equipment_signoff_systemcode;
  this_signoffs = this_contact['FieldValues'][signoff_idx]; 

  indiv_signoff_ids  = [];
  $('.signoff_item_div').find('input:checked').each(function() { 
    //
    // <div id="cid_50537517" class="form-check signoff_item_div">  
    // <input type="checkbox" class="form-check-input" id="fid_11968623" checked="checked">   
    //                   we store the field id in the DOM  ^^^^^^^^^^^^
    tid = this.id.replace('fid_','');
    //                  important:  vvvvvvvv
    indiv_signoff_ids.push( { 'Id': parseInt(tid), 'Label': $(this).next('label').text() });
  });

  // indiv_signoff_ids  
  // "[{"Id":"11968550"},{"Id":"11968623"}]" ....

  // compose what will become the json 
  // we send up to WA...
  wa_put_data = 
    {
      'Id' : this_contact_id ,
      'FieldValues' : 
      [{ 
        'FieldName' : 'EquipmentSignoffs',
        'SystemCode' : window.wautils_equipment_signoff_systemcode,
        'Value' : 
        indiv_signoff_ids

      }]
    }
  // .. but we send it via flask web server
  // all of wa_put_data will be sent to the flask server under 'put_data':
  flask_put_data = {
    'endpoint':'/accounts/$accountid/contacts/'  + this_contact_id,
    'put_data':wa_put_data 
  };

  $.ajax({
    type: 'PUT',
    url  : '/api/v1/wa_put_any_endpoint',
    data :  JSON.stringify(flask_put_data),
    beforeSend: () => { show_loader(); }, 
    success: (j) => { 
      if (j['error'] == 1) {
        hide_loader();
        m(j['error_message'],'warning');
        return false;
      }
      hide_loader().then(()=>{m(''); m('signoffs successfully updated','success')});
      // update contact locally:
      $.each(window.wautils_contacts[0].Contacts,function(k,v) {
        if (v['Id'] == this_contact_id) {
          // find the contact we are working on.. 
          $.each($(this)[0]['FieldValues'],function(kk,vv) {
            // then find 'EquipmentSignoffs' in their entry..
            if (vv['FieldName'] != 'NL Signoffs and Categories') 
              return true;
            // and replace it with what we sent up to WA
            $(this)[0]['Value'] = wa_put_data['FieldValues'][0]['Value'] 
          });
        }
      });
    },
    failure: (errMsg) => { alert("FAIL:" + errMsg); },
    error: (xh,ts,et) =>  { alert("FAIL:" + u + ' ' + et); },
    contentType: 'application/json; charset=utf-8',
    dataType : 'json', // we want to see json as a response
    processData: false
  });
}

function get_events() {
  // get contacts list
  // https://app.swaggerhub.com/apis-docs/WildApricot/wild-apricot_public_api/2.1.0#/Contacts/GetContactsList
  fep  = $.param({
    '$filter':'IsUpcoming eq True',
    '$sort':'ByStartDate asc'
  } );
  ep = $.param( {'endpoint':'accounts/$accountid/events/?' + fep});
  return new Promise(function(resolve,reject) {
    u  = '/api/v1/wa_get_any_endpoint',
      $.ajax({
        type: 'GET',
        url  : u,
        // string '$accountid' will get replaced with real account id on server
        // 'ByStartDate asc' doesn't seem to work
        //data : $.param({'endpoint':'accounts/$accountid/events/?&$filter=IsUpcoming%20eq%20true&$sort=ByStartDate%20asc'}),
        //data : $.param( {'endpoint':'accounts/$accountid/events/?%24async=false&%24filter=IsUpcoming%20eq%20True&%24sort=ByStartDate%20asc'}),
        data : ep,
        success: (j) => { 
          window.wautils_events  = j; // save for later
          process_events(window.wautils_events);
          resolve();  
        }, 
        failure: (errMsg) => { alert("FAIL:" + errMsg); },
        error: (xh,ts,et) =>  { alert("FAIL:" + u + ' ' + et); },
        contentType: false,
        processData: false
      });

  });

}

function get_event_registrations(event_id) {
  // get contacts list
  // https://app.swaggerhub.com/apis-docs/WildApricot/wild-apricot_public_api/2.1.0#/Contacts/GetContactsList
  fep  = $.param({
    'eventId':event_id,
    'includeWaitList':'true',
    '$async':'false'
  } );
  ep = $.param( {'endpoint':'accounts/$accountid/eventregistrations?' + fep});
  return new Promise(function(resolve,reject) {
    u  = '/api/v1/wa_get_any_endpoint',
      $.ajax({
        type: 'GET',
        url  : u,
        data : ep,
        success: (j) => { 
          window.wautils_event_registrations  = j; // save for later
          process_event_registrations(window.wautils_event_registrations);
          resolve();  
        }, 
        failure: (errMsg) => { alert("FAIL:" + errMsg); },
        error: (xh,ts,et) =>  { alert("FAIL:" + u + ' ' + et); },
        contentType: false,
        processData: false
      });

  });

}

function emit_event_item(v) {

  o += '<td>'
  o += '<p>' + v  + '</p>';
  o += '</td>'

  return o;
}

function process_event_registrations(j) {



  if (j['error'] == 1) {
    m(j['error_message'],'warning');
  } else  {

    o = '';
    o += '<h3>Event Registrations</h3>';
    o += '<table id="events_table"></table>'

    o += '<pre>';
    o += JSON.stringify(j,null,'\t');
    o += '</pre>';

    $('#maindiv').html(o);



    d = [];
    $.each(j,(k,v) => {
      console.log(JSON.stringify(v,null,'\t'));

      $.each(v.RegistrationFields,(kk,vv) => {

        /*


      "FieldName": "First name",
      "FieldName": "Last name",
      "FieldName": "Organization",
      "FieldName": "Email",
      "FieldName": "Phone",
      "FieldName": "Spaceman ID",
      "FieldName": "Badge Number",
      "FieldName": "Notes",

        vv.FieldName
        vv.Value
        */
      });
    });


  }


}

function process_events(j) {


  if (j['error'] == 1) {
    m(j['error_message'],'warning');
  } else  {

    o = '';
    o += '<h3>Upcoming Events</h3>';

    o += '<table id="events_table"></table>'

    $('#maindiv').html(o);

    d  = []; 
    $.each(j[0]['Events'],(k,v) => {
      d.push({
        Button                      : '<button class="btn btn-primary btn-sm m-1 event_row_edit_btn" id="'+v.Id+'">?</button>',
        Id                          : v.Id,
        Name                        : '<b>' + v.Name + '</b>',
        AccessLevel                 : v.AccessLevel,
        ConfirmedRegistrationsCount : v.ConfirmedRegistrationsCount,
        StartDate                   : v.StartDate.replace('T',' '),
        Location                    : v.Location,
        RegistrationsLimit          : v.Registrations,
        Tags                        : v.Tags
      });
    });


    // https://bootstrap-table.com/docs/getting-started/usage/#via-javascript

    $('#events_table').bootstrapTable(
      {
        search      : true,      // Whether to display table search
        showColumns : true,
        uniqueId    : "id",    // The unique identifier for each row, usually the primary key column
        showToggle  : true , // Whether to display the toggle buttons for detail view and list view
        sortName    : "StartDate",
        sortOrder   : "asc",

        columns: [
          {
            field: 'Button',
          }, {
            title: 'Id',
            field: 'Id',
            sortable: true,
          }, {
            title: 'Name',
            field: 'Name',
            sortable: true,
          }, {
            title: 'Visibility',
            field: 'AccessLevel',
          }, { 
            title: 'Regi-<br> strations',
            field: 'ConfirmedRegistrationsCount',
            width: '100px',
            sortable: true,

          }, {
            title: 'Start Date',
            field: 'StartDate',
            sortable: true,
          }, { 
            title: 'Location',
            field: 'Location',
            sortable: true,

          }, { 
            title: 'Registrations Limit',
            field: 'RegistrationsLimit',
            sortable: true,

          }, {

            title: 'Tags',
            field: 'Tags',
            sortable: true,
          }, 
        ],
        data : d 

      });

    $('#events_table').bootstrapTable('hideColumn','Id');
    $('#events_table').bootstrapTable('hideColumn','RegistrationsLimit');
    $('#events_table').bootstrapTable('hideColumn','AccessLevel');



  }
}

// initialize global storage
if(window.wautils_contact_ids == undefined ) window.wautils_contact_ids = [];
if(window.wautils_contact_fields == undefined ) window.wautils_contact_fields= [];
if(window.wautils_contacts == undefined ) window.wautils_contacts = [];
if(window.wautils_contact_index_list == undefined ) window.wautils_contact_index_list = [];
if(window.wautils_equipment_signoff_systemcode  == undefined ) window.wautils_equipment_signoff_systemcode = [];
if(window.wautils_events == undefined ) window.wautils_events = [];
if(window.wautils_event_registrations == undefined ) window.wautils_event_registrations = [];
if(window.wautils_membershiplevels == undefined ) window.wautils_membershiplevels = [];


// implement signoffs
if (document.getElementsByTagName("title")[0].innerHTML == 'signoffs') {
  hide_maindiv()
    .then(show_loader)
    .then(get_signoffs)
    .then(get_contacts)
    .then(hide_loader)
    .then(show_maindiv);
  return 0;
} 

// implement events
if (document.getElementsByTagName("title")[0].innerHTML == 'events') {

  hide_maindiv()
    .then(show_loader)
    .then(get_events)
    .then(hide_loader)
    .then(show_maindiv)
    .then($ => { });
  return 0;
} 
// implement members 
if (document.getElementsByTagName("title")[0].innerHTML == 'members') {
  hide_maindiv()
    .then(show_loader)
    .then(get_membershiplevels)
    .then(get_contacts)
    .then(hide_loader)
    .then(show_maindiv);

  return 0;
} 

});

});

