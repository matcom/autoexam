class ListadosController < ApplicationController
  before_action :set_listado, only: [:show, :edit, :update, :destroy]

  def edit
  end

  def update
    respond_to do |format|
      if @listado.update(listado_params)
        format.html { redirect_to @listado.asignatura, notice: 'Listado was successfully updated.' }
        format.json { head :no_content }
      else
        format.html { render action: 'edit' }
        format.json { render json: @listado.errors, status: :unprocessable_entity }
      end
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_listado
      @listado = Listado.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def listado_params
      params.require(:listado).permit(:asignatura_id, :estudiantes)
    end
end
