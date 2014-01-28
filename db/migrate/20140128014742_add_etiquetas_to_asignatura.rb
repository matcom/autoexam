class AddEtiquetasToAsignatura < ActiveRecord::Migration
  def change
    add_column :asignaturas, :etiquetas, :string
  end
end
