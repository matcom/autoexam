class ClaseOpcion < ActiveRecord::Base
  belongs_to :opcion

  def is_correct?
    if self.correcta.nil?
      self.correcta = self.opcion.right
      self.save
    end
    self.correcta
  end
end
