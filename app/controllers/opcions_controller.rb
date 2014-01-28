class OpcionsController < ApplicationController
  before_action :set_opcion, only: [:show, :edit, :update, :destroy]

  def index
    @opcions = Opcion.all
  end

  def nueva_opcion
    @preguntum = Preguntum.find(params[:id])
    @opcion = Opcion.new
    @opcion.preguntum_id = @preguntum.id
    render :new
  end

  def edit
  end

  def create
    @opcion = Opcion.new(opcion_params)

    respond_to do |format|
      if @opcion.save
        format.html { redirect_to @opcion.preguntum, notice: 'Opcion was successfully created.' }
        format.json { render action: 'show', status: :created, location: @opcion }
      else
        format.html { render action: 'new' }
        format.json { render json: @opcion.errors, status: :unprocessable_entity }
      end
    end
  end

  def update
    respond_to do |format|
      if @opcion.update(opcion_params)
        format.html { redirect_to @opcion.preguntum, notice: 'Opcion was successfully updated.' }
        format.json { head :no_content }
      else
        format.html { render action: 'edit' }
        format.json { render json: @opcion.errors, status: :unprocessable_entity }
      end
    end
  end

  def destroy
    pregunta = @opcion.preguntum
    @opcion.destroy

    respond_to do |format|
      format.html { redirect_to pregunta }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_opcion
      @opcion = Opcion.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def opcion_params
      params.require(:opcion).permit(:preguntum_id, :titulo, :right)
    end
end
