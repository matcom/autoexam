class ClavePregunta < ActiveRecord::Base

  def clave(opcion)
    ClaseOpcion.where(:opcion_id => opcion.id).where(:clave_preguntum_id => self.id).first_or_create
  end
end
