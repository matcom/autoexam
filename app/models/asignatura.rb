class Asignatura < ActiveRecord::Base

  def listado_de_etiquetas
    self.etiquetas.to_s.split(',').map {|e| e.strip }
  end
end
