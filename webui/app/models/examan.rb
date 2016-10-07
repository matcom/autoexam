class Examan < ActiveRecord::Base
  belongs_to :asignatura
  has_and_belongs_to_many :pregunta

  def listado_de_etiquetas
    self.etiquetas.to_s.split(',').map {|e| e.strip }
  end

  def clave(pregunta)
    cp = ClavePregunta.where(:preguntum_id => pregunta.id).where(:examan_id => self.id).first_or_create
    if cp.total_puntos.nil?
      cp.total_puntos = 1
      cp.minimo = 0
      cp.maximo = 1
    end
    return cp
  end

  def maximo(etiqueta)
    cantidades = preguntas_por_tema.to_s.split('|')
    for c in cantidades
      etiq, cant = c.split(':')
      if etiq == etiqueta
        return cant.to_i
      end
    end
    return 0
  end

  def preguntas_por_tema_hash
    hash = {}
    preguntas_por_tema.split("|").each do |pair|
      tag, count = pair.split(":")
      hash[tag] = count.to_i
    end
    hash
  end
end
