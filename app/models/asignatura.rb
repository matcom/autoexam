class Asignatura < ActiveRecord::Base
  has_many :pregunta
  has_one :listado
  has_many :examen
  after_save :ensure_listado

  def ensure_listado
    unless listado
      listado = Listado.new
      listado.asignatura_id = self.id
      listado.save
    end
  end

  def listado_de_etiquetas
    self.etiquetas.to_s.split(',').map {|e| e.strip }
  end
end
