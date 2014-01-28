class Examan < ActiveRecord::Base
  belongs_to :asignatura
  has_and_belongs_to_many :pregunta

  def listado_de_etiquetas
    self.etiquetas.to_s.split(',').map {|e| e.strip }
  end
end
