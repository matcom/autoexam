class ClavePregunta < ActiveRecord::Base

  def clave(opcion)
    co = ClaseOpcion.where(:opcion_id => opcion.id).where(:clave_preguntum_id => self.id).first
  	if co.nil?
  		co = ClaseOpcion.create(:opcion_id => opcion.id, :clave_preguntum_id => self.id)
  		co.correcta = co.opcion.right || false
  		multiple = co.opcion.preguntum.multiple || false
	  	if multiple
	  		if co.correcta
	  			co.puntos_bien = (self.total_puntos * 1.0 / co.opcion.preguntum.opcions.count)
  				co.puntos_mal = 0
  			else
	  			co.puntos_mal = (self.total_puntos * 1.0 / co.opcion.preguntum.opcions.count)
  				co.puntos_bien = 0
	  		end
  		else
  			if co.correcta
	  			co.puntos_bien = 1
	  			co.puntos_mal = 0
  			else
  				co.puntos_bien = 0
  				co.puntos_mal = 0 
	  		end
	  	end
	  	co.save
    end
  	return co
  end
end
