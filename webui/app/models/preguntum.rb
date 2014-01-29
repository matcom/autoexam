class Preguntum < ActiveRecord::Base
  belongs_to :asignatura
  has_many :opcions
  has_and_belongs_to_many :examen

  def listado_de_etiquetas
    self.etiquetas.to_s.split(',').map {|e| e.strip }
  end

  def self.from_etiqueta(etiqueta)
    where('etiquetas like ?', '%' + etiqueta + '%')
  end

  def self.ordenadas
    order(:id)
  end

  def titulo_con_numero(number)
    "##{number} - #{titulo}"
  end

end
