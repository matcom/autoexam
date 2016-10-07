class Preguntum < ActiveRecord::Base
  belongs_to :asignatura
  has_many :opcions
  has_and_belongs_to_many :examen
  validates_presence_of :titulo

  def listado_de_etiquetas
    self.etiquetas.to_s.split(',').map {|e| e.strip }
  end

  def self.from_etiqueta(etiqueta)
    preguntas = self.all
    result = []
    preguntas.each do |preg|
      list = preg.etiquetas.split(',').map { |s| s.strip }
      result << preg if !list.index(etiqueta).nil?
    end
    return result
  end

  def self.ordenadas
    order(:id)
  end

  def titulo_con_numero(number)
    "##{number} - #{titulo}"
  end

end
