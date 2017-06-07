/**
 * Created by Ale (Harambe's #1 follower) on 27-05-2017.
 */
function crearFormulario(INtipo) {
    var tipo = INtipo;
    //alert("se crea formulario admin");
	document.getElementById('formasDePago2').innerHTML="";
	document.getElementById('divHoraIni').innerHTML="";
	document.getElementById('divHoraFin').innerHTML="";

   if(tipo==2 || tipo== 3){
       //formas de pago
        var HTMLformasDePago = '<label for="formasDePago2">Seleccione sus formas de pago:</label>'+
                                    '<div class="row"></div>'+
                                    '<div class="row"></div>'+
									'<p>'+
									'<input type="checkbox" id="forma0" value="0"/>'+
									'<label for="forma0">Efectivo</label>'+
									'</p>'+
									'<p>'+
									'<input type="checkbox" id="forma1" value="1"/>'+
									'<label for="forma1">Tarjeta de Crédito</label>'+
									'</p>'+
									'<p>'+
									'<input type="checkbox" id="forma2" value="2"/>'+
									'<label for="forma2">Tarjeta de Débito</label>'+
									'</p>'+
									'<p>'+
									'<input type="checkbox" id="forma3" value="3"/>'+
									'<label for="forma3">Tarjeta Junaeb</label>'+
									'</p>';
        document.getElementById('formasDePago2').innerHTML=HTMLformasDePago;}


    if(tipo==2){
        var HTMLhoraIni='<i class="material-icons prefix">alarm</i>'+
								  '<input name="horaIni" id="horaIni" type="time" class="active validate" value="00:00">';

        var HTMLhoraFin='<i class="material-icons prefix">alarm</i>'+
								   '<input name="horaFin" id="horaFin" type="time" class="active validate" value="00:00">';

        document.getElementById('divHoraIni').innerHTML=HTMLhoraIni;
        document.getElementById('divHoraFin').innerHTML=HTMLhoraFin;}

}


function matchTipe(tipo){
    var res = "";
    switch(tipo){
        case 0: res = "admin";break;
        case 1: res = "alumno";break;
        case 2: res = "fijo";break;
        case 3: res = "ambulante";break;}
    return res;}

function generateModal(nombre,INtipo,email,avatar,contraseña,horaIni,horaFin,formas,id){
    document.getElementById("titulo").innerHTML="Datos de "+nombre;
    document.getElementById("name").value=nombre;
    document.getElementById("password").value=contraseña;
    document.getElementById("email").value=email;
    //document.getElementById('type').value=INtipo;

    var tipo = INtipo;
    crearFormulario(INtipo);
    document.getElementById("selectLabel").innerHTML="Tipo actual: "+ matchTipe(tipo);
    document.getElementById("fileName").value = avatar.split("/")[1];
    document.getElementById("avatarActual").src = "../static/media/"+avatar;


  if(tipo==2) {
    document.getElementById("horaIni").value=horaIni;
    document.getElementById("horaFin").value=horaFin;
  }

  if(tipo==2 || tipo== 3) {
      var array = JSON.parse("[" + formas + "]");
      for(var i=0;i<array.length;i++){
          var forma="forma"+array[i];
          document.getElementById(forma).checked =true;
      }
  }

   document.getElementById("type").selectedIndex = INtipo;
/*
 alert("THE END IS HERE");
    for(var i=0; i < document.getElementById("type").options.length; i++)
  {
    if(document.getElementById("type").options[i].value === INtipo) {
        alert("THE END IS HERE");
      document.getElementById("type").selectedIndex = i;
      break;
    }
  }
*/
   document.getElementById("userID").value = id;
}



function alertar(a){alert(a);}

function crearTabla(listaIn){
    var usuarios = listaIn;
    var largo = usuarios.length;
    for(var i=0;i<largo;i++){
        var uId = usuarios[i][0];
        var uNombre = usuarios[i][1];
        var uEmail = usuarios[i][2];
        var uTipoRaw = usuarios[i][3];
        var uTipo = matchTipe(usuarios[i][3]);
        var uAvatar = usuarios[i][4];
        var uActivo = usuarios[i][5];
        var uFormas = usuarios[i][6];
        var uHoraIni = usuarios[i][7];
        var uHoraFin = usuarios[i][8];
        var uContraseña = usuarios[i][9];
        var modalId = "modal"+i;
        //alertar(uId);
       // generateModal(modalId,uId,uNombre,uEmail,uTipoRaw,uAvatar,uActivo,uFormas,uHoraIni,uHoraFin);
        var seccion = '<tr>'+
            '<td>'+uId+'</td>'+
            '<td>'+uNombre+'</td>'+
            '<td>'+uEmail+'</td>'+
            '<td>'+uTipo+'</td>'+
            '<td style="display:none;">'+uAvatar+'</td>'+
            '<td style="display:none;">'+uActivo+'</td>'+
            '<td id="Uformas" style="display:none;">'+uFormas+'</td>'+
            '<td style="display:none;">'+uHoraIni+'</td>'+
            '<td style="display:none;">'+uHoraFin+'</td>'+
            '<td style>'+'<a class="waves-effect waves-light" onclick=generateModal('+'"'+uNombre+'"'+
            ','+uTipoRaw+','+
            '"'+uEmail+'"'+','+
            '"'+uAvatar+'"'+','+
            '"'+uContraseña+'"'+','+
            '"'+uHoraIni+'"'+','+
            '"'+uHoraFin+'"'+','+
            '"'+uFormas+'"'+','+
            '"'+uId+'"'+
            ') href="#modal">Editar datos</a>'+'</td>'+
            '</tr>';
        document.getElementById('insertTabla').innerHTML += seccion;}
}