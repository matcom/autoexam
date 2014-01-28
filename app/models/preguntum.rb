class Preguntum < ActiveRecord::Base
  belongs_to :asignatura
  has_many :opcions

  def listado_de_etiquetas
    self.etiquetas.to_s.split(',').map {|e| e.strip }
  end
end
