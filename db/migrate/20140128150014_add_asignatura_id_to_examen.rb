class AddAsignaturaIdToExamen < ActiveRecord::Migration
  def change
    add_column :examen, :asignatura_id, :integer
  end
end
